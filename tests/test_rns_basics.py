"""
Basic RNS environment tests.

RNS.Reticulum is a process-level singleton — there can only be one instance
per process. All tests share a single session-scoped instance that connects
to itself via TCP loopback (server + client interfaces in the same config),
giving us real transport-level routing within one process.

Run: pixi run test
"""

import os
import time
import threading
import pytest
import RNS

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
        """Same identity + same naming always gives the same hash."""
        identity = RNS.Identity()
        dest_a = RNS.Destination(identity, RNS.Destination.IN, RNS.Destination.SINGLE, "myapp", "svc")
        dest_b = RNS.Destination(identity, RNS.Destination.IN, RNS.Destination.SINGLE, "myapp", "svc")
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
    def test_announce_triggers_handler(self, rns):
        """Announce from a local destination is received by a registered handler."""
        received = threading.Event()
        received_hash = []

        class Handler:
            aspect_filter = "playground.ann_test_1"

            def received_announce(self, destination_hash, announced_identity, app_data):
                received_hash.append(destination_hash)
                received.set()

        RNS.Transport.register_announce_handler(Handler())

        identity = RNS.Identity()
        dest = RNS.Destination(
            identity, RNS.Destination.IN, RNS.Destination.SINGLE,
            "playground", "ann_test_1"
        )
        dest.announce()

        assert received.wait(timeout=5), "Announce not received within 5s"
        assert received_hash[0] == dest.hash

    def test_announce_carries_app_data(self, rns):
        """app_data bytes are delivered correctly through the announce."""
        received_data = []
        done = threading.Event()

        class Handler:
            aspect_filter = "playground.ann_test_2"

            def received_announce(self, destination_hash, announced_identity, app_data):
                received_data.append(app_data)
                done.set()

        RNS.Transport.register_announce_handler(Handler())

        identity = RNS.Identity()
        dest = RNS.Destination(
            identity, RNS.Destination.IN, RNS.Destination.SINGLE,
            "playground", "ann_test_2"
        )
        dest.announce(app_data=b"hello:world:42")

        assert done.wait(timeout=5)
        assert received_data[0] == b"hello:world:42"

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
        """After an announce, the identity is recallable by destination hash."""
        done = threading.Event()

        class Handler:
            aspect_filter = "playground.ann_test_recall"

            def received_announce(self, destination_hash, announced_identity, app_data):
                done.set()

        RNS.Transport.register_announce_handler(Handler())

        identity = RNS.Identity()
        dest = RNS.Destination(
            identity, RNS.Destination.IN, RNS.Destination.SINGLE,
            "playground", "ann_test_recall"
        )
        dest.announce()
        done.wait(timeout=5)

        recalled = RNS.Identity.recall(dest.hash)
        assert recalled is not None
        assert recalled.hash == identity.hash


# ---------------------------------------------------------------------------
# Tests: packet send/receive
# ---------------------------------------------------------------------------

class TestPackets:
    def test_packet_delivered_with_proof(self, rns):
        """Send a packet to a local destination; verify delivery proof arrives."""
        delivered = threading.Event()
        received_messages = []

        server_identity = RNS.Identity()
        server_dest = RNS.Destination(
            server_identity, RNS.Destination.IN, RNS.Destination.SINGLE,
            "playground", "pkt_test_1"
        )
        server_dest.set_proof_strategy(RNS.Destination.PROVE_ALL)
        server_dest.set_packet_callback(lambda msg, pkt: received_messages.append(msg))
        server_dest.announce()

        # Wait for path to appear in routing table
        deadline = time.time() + 6
        while not RNS.Transport.has_path(server_dest.hash):
            assert time.time() < deadline, "Path never appeared in routing table"
            time.sleep(0.1)

        recalled = RNS.Identity.recall(server_dest.hash)
        assert recalled is not None

        outgoing = RNS.Destination(
            recalled, RNS.Destination.OUT, RNS.Destination.SINGLE,
            "playground", "pkt_test_1"
        )
        packet = RNS.Packet(outgoing, b"test_payload")
        receipt = packet.send()
        receipt.set_timeout(5.0)
        receipt.set_delivery_callback(lambda r: delivered.set())

        assert delivered.wait(timeout=6), "Delivery proof never arrived"
        assert received_messages[0] == b"test_payload"

    def test_multiple_packets(self, rns):
        """Send several packets and confirm all are received."""
        count_expected = 3
        received = []
        all_done = threading.Event()

        server_identity = RNS.Identity()
        server_dest = RNS.Destination(
            server_identity, RNS.Destination.IN, RNS.Destination.SINGLE,
            "playground", "pkt_test_multi"
        )
        server_dest.set_proof_strategy(RNS.Destination.PROVE_ALL)

        def on_pkt(msg, pkt):
            received.append(msg)
            if len(received) >= count_expected:
                all_done.set()

        server_dest.set_packet_callback(on_pkt)
        server_dest.announce()

        deadline = time.time() + 6
        while not RNS.Transport.has_path(server_dest.hash):
            assert time.time() < deadline, "Path never appeared"
            time.sleep(0.1)

        recalled = RNS.Identity.recall(server_dest.hash)
        outgoing = RNS.Destination(
            recalled, RNS.Destination.OUT, RNS.Destination.SINGLE,
            "playground", "pkt_test_multi"
        )

        for i in range(count_expected):
            pkt = RNS.Packet(outgoing, f"msg_{i}".encode())
            pkt.send()
            time.sleep(0.05)

        assert all_done.wait(timeout=6), f"Only got {len(received)}/{count_expected} packets"
        payloads = [m.decode() for m in received]
        for i in range(count_expected):
            assert f"msg_{i}" in payloads


# ---------------------------------------------------------------------------
# Tests: LXMF messaging
# ---------------------------------------------------------------------------

class TestLXMF:
    def test_lxmf_direct_delivery(self, rns, tmp_path):
        """Send an LXMF message and confirm it is delivered with correct content."""
        import LXMF

        storage_a = str(tmp_path / "lxmf_a")
        storage_b = str(tmp_path / "lxmf_b")

        router_a = LXMF.LXMRouter(storagepath=storage_a, autopeer=False)
        router_b = LXMF.LXMRouter(storagepath=storage_b, autopeer=False)

        id_a = RNS.Identity()
        id_b = RNS.Identity()

        source = router_a.register_delivery_identity(id_a, display_name="NodeA")
        dest_b = router_b.register_delivery_identity(id_b, display_name="NodeB")

        received = threading.Event()
        received_content = []

        def on_delivery(message):
            received_content.append(message.content_as_string())
            received.set()

        router_b.register_delivery_callback(on_delivery)
        dest_b.announce()

        # Wait for path
        deadline = time.time() + 6
        while not RNS.Transport.has_path(dest_b.hash):
            assert time.time() < deadline, "Path to NodeB never appeared"
            time.sleep(0.1)

        b_identity = RNS.Identity.recall(dest_b.hash)
        lxmf_dest = RNS.Destination(
            b_identity, RNS.Destination.OUT, RNS.Destination.SINGLE,
            "lxmf", "delivery"
        )

        msg = LXMF.LXMessage(lxmf_dest, source, "Hello LXMF")
        msg.desired_method = LXMF.LXMessage.DIRECT
        router_a.handle_outbound(msg)

        assert received.wait(timeout=8), "LXMF message not delivered within 8s"
        assert received_content[0] == "Hello LXMF"

    def test_lxmf_fields_preserved(self, rns, tmp_path):
        """LXMF Fields dict is delivered intact."""
        import LXMF

        storage_a = str(tmp_path / "lxmf_fa")
        storage_b = str(tmp_path / "lxmf_fb")

        router_a = LXMF.LXMRouter(storagepath=storage_a, autopeer=False)
        router_b = LXMF.LXMRouter(storagepath=storage_b, autopeer=False)

        id_a = RNS.Identity()
        id_b = RNS.Identity()

        source = router_a.register_delivery_identity(id_a, display_name="SensorNode")
        dest_b = router_b.register_delivery_identity(id_b, display_name="Collector")

        received = threading.Event()
        received_fields = []

        def on_delivery(message):
            received_fields.append(message.get_fields())
            received.set()

        router_b.register_delivery_callback(on_delivery)
        dest_b.announce()

        deadline = time.time() + 6
        while not RNS.Transport.has_path(dest_b.hash):
            assert time.time() < deadline, "Path to Collector never appeared"
            time.sleep(0.1)

        b_identity = RNS.Identity.recall(dest_b.hash)
        lxmf_dest = RNS.Destination(
            b_identity, RNS.Destination.OUT, RNS.Destination.SINGLE,
            "lxmf", "delivery"
        )

        fields = {"type": "telemetry", "temp_c": 22.5, "node": "garden_shed"}
        msg = LXMF.LXMessage(lxmf_dest, source, "", fields=fields)
        msg.desired_method = LXMF.LXMessage.DIRECT
        router_a.handle_outbound(msg)

        assert received.wait(timeout=8), "LXMF fields message not delivered"
        f = received_fields[0]
        assert f["type"] == "telemetry"
        assert f["temp_c"] == 22.5
        assert f["node"] == "garden_shed"
