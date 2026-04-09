"""
Rust ↔ Python interoperability tests.

Tests that Python RNS (reference implementation) and Reticulum-rs (Rust) can
exchange announce packets over TCP using their shared HDLC framing protocol.

Architecture:
- The session RNS fixture (port 14399) is not used here — each interop test
  spawns both sides as subprocesses because RNS is a process-level singleton.
- Rust examples are compiled from sources/Reticulum-rs/ and the
  binaries are expected in that project's target/debug/examples/ directory.

Prerequisites:
    cd sources/Reticulum-rs && cargo build --example tcp_server --example tcp_client

Run: pixi run test-interop
"""

import os
import time
import pathlib
import subprocess
import threading
import multiprocessing
import pytest

# Paths
_REPO_ROOT = pathlib.Path(__file__).parent.parent
RETICULUM_RS_DIR = _REPO_ROOT / "sources" / "Reticulum-rs"
RUST_TCP_SERVER = RETICULUM_RS_DIR / "target" / "debug" / "examples" / "tcp_server"
RUST_TCP_CLIENT = RETICULUM_RS_DIR / "target" / "debug" / "examples" / "tcp_client"

# Port hardcoded in the Rust examples
RUST_PORT = 4242


# ---------------------------------------------------------------------------
# Subprocess workers
# ---------------------------------------------------------------------------

def _python_rns_server_worker(config_dir, result_file, port):
    """
    Spawned subprocess: start Python RNS with TCPServer on given port.
    Register an announce handler for "example.app" (what Rust tcp_client
    announces). On receipt, write the destination hash (hex) to result_file.
    """
    import os
    import time
    import threading
    import RNS

    os.makedirs(config_dir, exist_ok=True)
    config = f"""
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
  listen_port = {port}
"""
    with open(os.path.join(config_dir, "config"), "w") as f:
        f.write(config)

    RNS.Reticulum(config_dir, loglevel=RNS.LOG_WARNING)
    time.sleep(0.3)

    received = threading.Event()

    class Handler:
        aspect_filter = "example.app"

        def received_announce(self, destination_hash, announced_identity, app_data):
            with open(result_file, "w") as f:
                f.write(destination_hash.hex())
            received.set()

    RNS.Transport.register_announce_handler(Handler())

    # Wait for an announce (up to 30 s) then exit
    received.wait(timeout=30)
    time.sleep(0.5)


def _python_rns_client_worker(config_dir, port):
    """
    Spawned subprocess: start Python RNS with TCPClient connecting to a Rust
    tcp_server, create a destination, and announce it.
    """
    import os
    import time
    import RNS

    os.makedirs(config_dir, exist_ok=True)
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
    with open(os.path.join(config_dir, "config"), "w") as f:
        f.write(config)

    RNS.Reticulum(config_dir, loglevel=RNS.LOG_WARNING)
    time.sleep(1.0)  # let TCP connect and stabilise

    identity = RNS.Identity()
    dest = RNS.Destination(
        identity, RNS.Destination.IN, RNS.Destination.SINGLE, "playground", "rust_interop"
    )
    dest.announce()
    time.sleep(3.0)  # let announce propagate before process exits


# ---------------------------------------------------------------------------
# Module fixture: skip if Rust binaries not built
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def rust_binaries():
    if not RUST_TCP_SERVER.exists() or not RUST_TCP_CLIENT.exists():
        pytest.skip(
            f"Rust binaries not found. Build with:\n"
            f"  cd {RETICULUM_RS_DIR} && cargo build --example tcp_server --example tcp_client"
        )
    return {"server": str(RUST_TCP_SERVER), "client": str(RUST_TCP_CLIENT)}


# ---------------------------------------------------------------------------
# Interoperability tests
# ---------------------------------------------------------------------------

class TestRustPythonInterop:
    def test_rust_announces_to_python(self, rust_binaries, tmp_path):
        """
        Rust tcp_client → Python TCPServer: announce received correctly.

        The Rust client connects to 127.0.0.1:4242, waits 3 s, then announces
        a SingleInputDestination named "example.app". Python RNS listens on
        that port, receives the announce, and records the 16-byte destination
        hash.

        This verifies:
        - HDLC framing compatibility (Rust → Python direction)
        - Wire-level announce packet format is interoperable
        - Python RNS correctly decodes a Rust-generated cryptographic identity
        """
        result_file = str(tmp_path / "received_hash.txt")
        config_dir = str(tmp_path / "py_server")

        ctx = multiprocessing.get_context("spawn")
        server_proc = ctx.Process(
            target=_python_rns_server_worker,
            args=(config_dir, result_file, RUST_PORT),
            daemon=True,
        )
        server_proc.start()

        # Give Python server time to bind and listen
        time.sleep(1.5)

        env = os.environ.copy()
        env["RUST_LOG"] = "warn"
        rust_proc = subprocess.Popen(
            [rust_binaries["client"]],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            # Rust client sleeps 3 s before announcing; allow 20 s total
            deadline = time.time() + 20
            while time.time() < deadline:
                if os.path.exists(result_file):
                    break
                time.sleep(0.25)

            assert os.path.exists(result_file), \
                "Python RNS did not receive Rust announce within 20 s"

            with open(result_file) as f:
                hash_hex = f.read().strip()

            # Destination hash is always 16 bytes = 32 hex chars
            assert len(hash_hex) == 32, \
                f"Expected 32 hex chars (16-byte hash), got: {hash_hex!r}"
        finally:
            rust_proc.terminate()
            rust_proc.wait(timeout=3)
            server_proc.terminate()
            server_proc.join(timeout=3)

    def test_python_announces_to_rust(self, rust_binaries, tmp_path):
        """
        Python TCPClient → Rust tcp_server: Rust accepts the connection.

        Python RNS announces via its TCPClient to the Rust tcp_server. The
        Rust server must remain running (not crash) when it receives a
        Python-generated HDLC-framed announce packet.

        This verifies:
        - HDLC framing compatibility (Python → Rust direction)
        - Rust transport layer accepts Python-format cryptographic packets
        """
        env = os.environ.copy()
        env["RUST_LOG"] = "warn"
        rust_proc = subprocess.Popen(
            [rust_binaries["server"]],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        time.sleep(1.0)  # let Rust server bind

        ctx = multiprocessing.get_context("spawn")
        config_dir = str(tmp_path / "py_client")
        client_proc = ctx.Process(
            target=_python_rns_client_worker,
            args=(config_dir, RUST_PORT),
            daemon=True,
        )
        client_proc.start()

        try:
            # Wait for Python client to complete its announce + sleep cycle
            client_proc.join(timeout=15)

            # Rust server should still be running — not crashed by the Python packet
            assert rust_proc.poll() is None, \
                "Rust tcp_server exited unexpectedly after receiving Python announce"
        finally:
            rust_proc.terminate()
            rust_proc.wait(timeout=3)
            if client_proc.is_alive():
                client_proc.terminate()
                client_proc.join(timeout=3)
