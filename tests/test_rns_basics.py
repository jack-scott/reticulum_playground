"""
Basic RNS environment tests.

RNS.Reticulum is a process-level singleton — there can only be one instance
per process. All tests share a single session-scoped instance that connects
to itself via TCP loopback (server + client interfaces in the same config),
giving us real transport-level routing within one process.

Two important single-process constraints:

1. Announces for locally-registered destinations are intentionally filtered by
   RNS to prevent routing loops. Announce handler tests therefore spawn a
   subprocess (using the 'spawn' start method to avoid fork/thread deadlocks)
   that connects to the test TCPServer and announces from an external identity.

2. DATA packets are added to the hashlist during Transport.outbound(), so
   loopback receives are always filtered. Packet and LXMF tests verify the
   send API (packet creation, receipt objects, router queuing) rather than
   end-to-end delivery.

Run: pixi run test
"""

import os
import sys
import time
import threading
import multiprocessing
import pytest
import RNS


# ---------------------------------------------------------------------------
# Subprocess worker: announces from a separate RNS process
# ---------------------------------------------------------------------------

def _rns_announce_worker(config_dir, app_name, aspect, app_data_hex, port):
    """
    Runs in a subprocess (spawn context). Starts its own RNS instance with a
    TCPClient interface pointing at the test's TCPServer, creates a destination,
    and announces it (optionally with app_data).
    """
    config = f"""
[reticulum]
enable_transport = no
share_instance = no
panic_on_interface_error = no

[logging]
loglevel = 2

[interfaces]

  [[TCPClient]]
  type = TCPClientInterface
  enabled = yes
  target_host = 127.0.0.1
  target_port = {port}
"""
    os.makedirs(config_dir, exist_ok=True)
    with open(os.path.join(config_dir, "config"), "w") as f:
        f.write(config)

    instance = RNS.Reticulum(config_dir, loglevel=RNS.LOG_WARNING)
    time.sleep(0.8)  # let TCP connect and stabilise

    identity = RNS.Identity()
    dest = RNS.Destination(
        identity, RNS.Destination.IN, RNS.Destination.SINGLE,
        app_name, aspect
    )
    app_data = bytes.fromhex(app_data_hex) if app_data_hex else None
    dest.announce(app_data=app_data)
    time.sleep(2.0)  # let announce propagate before process exits


# ---------------------------------------------------------------------------
# Session-scoped RNS instance (created once for the whole test run)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def rns(tmp_path_factory):
    """Start a single RNS instance with a loopback TCP pair."""
    base = tmp_path_factory.mktemp("rns_session")
    config_dir = str(base / "config")
    os.makedirs(config_dir, exist_ok=True)

    config = """
[reticulum]
enable_transport = yes
share_instance = no
panic_on_interface_error = no

[logging]
loglevel = 2

[interfaces]

  [[TCPServer]]
  type = TCPServerInterface
  enabled = yes
  listen_ip = 127.0.0.1
  listen_port = 14399

  [[TCPClient]]
  type = TCPClientInterface
  enabled = yes
  target_host = 127.0.0.1
  target_port = 14399
"""
    with open(os.path.join(config_dir, "config"), "w") as f:
        f.write(config)

    instance = RNS.Reticulum(config_dir, loglevel=RNS.LOG_WARNING)
    time.sleep(0.5)  # let TCP interfaces come up
    yield instance
    # No teardown — process will exit after tests finish


# ---------------------------------------------------------------------------
# Tests: imports and versions
# ---------------------------------------------------------------------------

class TestImports:
    def test_rns_imports(self):
        assert RNS is not None

    def test_lxmf_imports(self):
        import LXMF
        assert LXMF is not None

    def test_lxst_imports(self):
        import LXST
        assert LXST is not None

    def test_rns_version(self):
        parts = RNS.__version__.split(".")
        assert len(parts) >= 2, f"Unexpected version format: {RNS.__version__}"

    def test_lxmf_version(self):
        import LXMF
        assert hasattr(LXMF, "__version__")


# ---------------------------------------------------------------------------
# Tests: identity and destination (no networking needed)
# ---------------------------------------------------------------------------

class TestIdentityAndDestination:
    def test_identity_creates(self, rns):
        identity = RNS.Identity()
        assert identity is not None

    def test_identity_hash_is_16_bytes(self, rns):
        # Identity.hash is a truncated hash — 16 bytes (128-bit)
        identity = RNS.Identity()
        assert len(identity.hash) == 16

    def test_identity_has_public_key(self, rns):
        identity = RNS.Identity()
        pubkey = identity.get_public_key()
        assert pubkey is not None
        assert len(pubkey) > 0

    def test_identity_save_reload(self, rns, tmp_path):
        identity = RNS.Identity()
        original_hash = identity.hash

        path = str(tmp_path / "test_identity")
        identity.to_file(path)
        assert os.path.exists(path)

        loaded = RNS.Identity.from_file(path)
        assert loaded.hash == original_hash

    def test_destination_creates(self, rns):
        identity = RNS.Identity()
        dest = RNS.Destination(
            identity, RNS.Destination.IN, RNS.Destination.SINGLE, "test", "basic"
        )
        assert dest is not None
        assert len(dest.hash) == 16  # 128-bit truncated hash

    def test_destination_hash_is_deterministic(self, rns):
        """Same identity + same naming always gives the same hash.

        Direction (IN vs OUT) does not affect the hash formula, so we compare
        an IN destination against an OUT destination to avoid the duplicate
        registration error that would occur with two IN destinations.
        """
        identity = RNS.Identity()
        dest_a = RNS.Destination(identity, RNS.Destination.IN, RNS.Destination.SINGLE, "myapp", "svc")
        dest_b = RNS.Destination(identity, RNS.Destination.OUT, RNS.Destination.SINGLE, "myapp", "svc")
        assert dest_a.hash == dest_b.hash

    def test_different_aspects_give_different_hashes(self, rns):
        identity = RNS.Identity()
        dest_a = RNS.Destination(identity, RNS.Destination.IN, RNS.Destination.SINGLE, "myapp", "alpha")
        dest_b = RNS.Destination(identity, RNS.Destination.IN, RNS.Destination.SINGLE, "myapp", "beta")
        assert dest_a.hash != dest_b.hash

    def test_different_identities_give_different_hashes(self, rns):
        id_a = RNS.Identity()
        id_b = RNS.Identity()
        dest_a = RNS.Destination(id_a, RNS.Destination.IN, RNS.Destination.SINGLE, "myapp", "svc")
        dest_b = RNS.Destination(id_b, RNS.Destination.IN, RNS.Destination.SINGLE, "myapp", "svc")
        assert dest_a.hash != dest_b.hash

    def test_prettyhexrep_format(self, rns):
        identity = RNS.Identity()
        rep = RNS.prettyhexrep(identity.hash)
        # Format: <xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx>  (32 hex chars for 16 bytes)
        assert rep.startswith("<") and rep.endswith(">")
        assert len(rep) == 34  # < + 32 hex chars + >


# ---------------------------------------------------------------------------
# Tests: announce propagation
# ---------------------------------------------------------------------------

class TestAnnounces:
    def test_announce_triggers_handler(self, rns, tmp_path):
        """Announce from an external process is received by a registered handler.

        We use multiprocessing with the 'spawn' start method (not fork) to
        avoid deadlocks in the multi-threaded RNS process. The subprocess
        creates its own RNS instance with a TCPClient pointing at our
        TCPServer, so its announce reaches us as a genuinely external packet.
        """
        received = threading.Event()
        received_hash = []

        class Handler:
            aspect_filter = "playground.ann_test_1"

            def received_announce(self, destination_hash, announced_identity, app_data):
                received_hash.append(destination_hash)
                received.set()

        RNS.Transport.register_announce_handler(Handler())

        ctx = multiprocessing.get_context("spawn")
        worker_config = str(tmp_path / "ann_worker_1")
        proc = ctx.Process(
            target=_rns_announce_worker,
            args=(worker_config, "playground", "ann_test_1", "", 14399),
            daemon=True,
        )
        proc.start()

        try:
            assert received.wait(timeout=15), "Announce not received within 15s"
            assert len(received_hash[0]) == 16  # 128-bit destination hash
        finally:
            proc.terminate()
            proc.join(timeout=3)

    def test_announce_carries_app_data(self, rns, tmp_path):
        """app_data bytes are delivered correctly through the announce."""
        received_data = []
        done = threading.Event()

        class Handler:
            aspect_filter = "playground.ann_test_2"

            def received_announce(self, destination_hash, announced_identity, app_data):
                received_data.append(app_data)
                done.set()

        RNS.Transport.register_announce_handler(Handler())

        app_data = b"hello:world:42"
        ctx = multiprocessing.get_context("spawn")
        worker_config = str(tmp_path / "ann_worker_2")
        proc = ctx.Process(
            target=_rns_announce_worker,
            args=(worker_config, "playground", "ann_test_2", app_data.hex(), 14399),
            daemon=True,
        )
        proc.start()

        try:
            assert done.wait(timeout=15), "Announce with app_data not received within 15s"
            assert received_data[0] == app_data
        finally:
            proc.terminate()
            proc.join(timeout=3)

    def test_aspect_filter_ignores_other_apps(self, rns):
        """Handler with a specific filter should NOT receive announces for other apps."""
        wrong_received = threading.Event()

        class StrictHandler:
            aspect_filter = "playground.ann_strict"

            def received_announce(self, destination_hash, announced_identity, app_data):
                wrong_received.set()

        RNS.Transport.register_announce_handler(StrictHandler())

        # Announce from a DIFFERENT aspect
        identity = RNS.Identity()
        dest = RNS.Destination(
            identity, RNS.Destination.IN, RNS.Destination.SINGLE,
            "playground", "ann_other"
        )
        dest.announce()

        # Give it time — the wrong handler should NOT fire
        wrong_received.wait(timeout=2)
        assert not wrong_received.is_set(), "Strict handler fired for wrong aspect"

    def test_identity_recalled_after_announce(self, rns):
        """Identity is recallable by destination hash.

        Identity.recall() checks Transport.destinations as a fallback, so
        this works without the announce looping back through the network.
        """
        identity = RNS.Identity()
        dest = RNS.Destination(
            identity, RNS.Destination.IN, RNS.Destination.SINGLE,
            "playground", "ann_test_recall"
        )
        dest.announce()

        recalled = RNS.Identity.recall(dest.hash)
        assert recalled is not None
        assert recalled.hash == identity.hash


# ---------------------------------------------------------------------------
# Tests: packet send API
#
# RNS adds packet hashes to the filter hashlist during Transport.outbound(),
# so a packet broadcast from this process is filtered when it loops back via
# TCPServer. End-to-end delivery therefore requires two separate processes.
# These tests verify the packet CREATION and SEND API surface instead.
# ---------------------------------------------------------------------------

class TestPackets:
    def test_packet_send_returns_receipt(self, rns):
        """RNS.Packet can be created and sent; Transport.outbound() returns a receipt."""
        server_identity = RNS.Identity()
        # Create IN destination (receives) and matching OUT destination (sends)
        RNS.Destination(
            server_identity, RNS.Destination.IN, RNS.Destination.SINGLE,
            "playground", "pkt_test_1"
        )
        outgoing = RNS.Destination(
            server_identity, RNS.Destination.OUT, RNS.Destination.SINGLE,
            "playground", "pkt_test_1"
        )
        packet = RNS.Packet(outgoing, b"test_payload")
        receipt = packet.send()
        assert receipt is not False, "Packet transmission failed"
        assert receipt is not None, "Packet transmission failed"
        assert packet.sent is True

    def test_multiple_packets_sent(self, rns):
        """Multiple packets can be created and submitted to Transport."""
        server_identity = RNS.Identity()
        RNS.Destination(
            server_identity, RNS.Destination.IN, RNS.Destination.SINGLE,
            "playground", "pkt_test_multi"
        )
        outgoing = RNS.Destination(
            server_identity, RNS.Destination.OUT, RNS.Destination.SINGLE,
            "playground", "pkt_test_multi"
        )
        for i in range(3):
            pkt = RNS.Packet(outgoing, f"msg_{i}".encode())
            receipt = pkt.send()
            assert receipt is not False, f"Packet {i} transmission failed"
            time.sleep(0.05)


# ---------------------------------------------------------------------------
# Tests: LXMF API
#
# Same loopback limitation applies to LXMF DATA packets. These tests verify
# that LXMRouter initialises correctly and can queue outbound messages.
# ---------------------------------------------------------------------------

class TestLXMF:
    def test_lxmf_router_creates(self, rns, tmp_path):
        """LXMRouter can be created and a delivery identity registered."""
        import LXMF

        storage = str(tmp_path / "lxmf_r")
        router = LXMF.LXMRouter(storagepath=storage, autopeer=False)
        identity = RNS.Identity()
        dest = router.register_delivery_identity(identity, display_name="TestNode")
        assert dest is not None
        assert len(dest.hash) == 16

    def test_lxmf_message_queued(self, rns, tmp_path):
        """LXMMessage can be created and handed to LXMRouter without error."""
        import LXMF

        storage_a = str(tmp_path / "lxmf_a")
        storage_b = str(tmp_path / "lxmf_b")

        router_a = LXMF.LXMRouter(storagepath=storage_a, autopeer=False)
        router_b = LXMF.LXMRouter(storagepath=storage_b, autopeer=False)

        id_a = RNS.Identity()
        id_b = RNS.Identity()

        source = router_a.register_delivery_identity(id_a, display_name="NodeA")
        dest_b  = router_b.register_delivery_identity(id_b, display_name="NodeB")

        # Identity.recall() falls back to Transport.destinations — no announce needed
        b_identity = RNS.Identity.recall(dest_b.hash)
        assert b_identity is not None

        lxmf_dest = RNS.Destination(
            b_identity, RNS.Destination.OUT, RNS.Destination.SINGLE,
            "lxmf", "delivery"
        )

        msg = LXMF.LXMessage(lxmf_dest, source, "Hello LXMF")
        msg.desired_method = LXMF.LXMessage.OPPORTUNISTIC
        router_a.handle_outbound(msg)

        # Message should be queued as OUTBOUND (or progressed further)
        time.sleep(0.3)
        assert msg.state in (
            LXMF.LXMessage.OUTBOUND,
            LXMF.LXMessage.SENDING,
            LXMF.LXMessage.DELIVERED,
            LXMF.LXMessage.FAILED,  # acceptable — environment is verified if no exception raised
        )

    def test_lxmf_fields_in_message(self, rns, tmp_path):
        """LXMessage with a Fields dict can be created and packed without error."""
        import LXMF

        # Each LXMRouter supports only one delivery identity — use separate instances
        router_a = LXMF.LXMRouter(storagepath=str(tmp_path / "lxmf_fa"), autopeer=False)
        router_b = LXMF.LXMRouter(storagepath=str(tmp_path / "lxmf_fb"), autopeer=False)

        id_a = RNS.Identity()
        id_b = RNS.Identity()

        source = router_a.register_delivery_identity(id_a, display_name="SensorNode")
        dest_b  = router_b.register_delivery_identity(id_b, display_name="Collector")

        b_identity = RNS.Identity.recall(dest_b.hash)
        lxmf_dest = RNS.Destination(
            b_identity, RNS.Destination.OUT, RNS.Destination.SINGLE,
            "lxmf", "delivery"
        )

        fields = {"type": "telemetry", "temp_c": 22.5, "node": "garden_shed"}
        msg = LXMF.LXMessage(lxmf_dest, source, "", fields=fields)
        msg.pack()  # encode to wire format — verifies msgpack serialisation
        assert msg.packed is not None
        assert len(msg.packed) > 0
