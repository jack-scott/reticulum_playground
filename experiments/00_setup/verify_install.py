#!/usr/bin/env python3
"""
Module 00 — Setup Verification

Verifies the RNS environment works correctly.
Starts Reticulum with a local config, generates an identity,
prints its hash, and exits cleanly.

Run: pixi run verify
  or: pixi run python experiments/00_setup/verify_install.py
"""

import sys
import os

# Keep RNS state local to this experiment
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "rns_config")

def main():
    print("Checking imports...")
    try:
        import RNS
        print(f"  rns         {RNS.__version__}")
    except ImportError as e:
        print(f"  ERROR: could not import RNS: {e}")
        sys.exit(1)

    try:
        import LXMF
        print(f"  lxmf        {LXMF.__version__}")
    except ImportError as e:
        print(f"  WARNING: could not import LXMF: {e}")

    try:
        import LXST
        version = getattr(LXST, "__version__", "installed")
        print(f"  lxst        {version}")
    except ImportError as e:
        print(f"  WARNING: could not import LXST: {e}")

    print()
    print("Starting Reticulum (local config)...")
    rns = RNS.Reticulum(CONFIG_PATH, loglevel=RNS.LOG_WARNING)

    print("Generating identity...")
    identity = RNS.Identity()
    print(f"  Identity hash : {RNS.prettyhexrep(identity.hash)}")
    print(f"  Config path   : {CONFIG_PATH}")
    print()

    print("Creating a test destination...")
    dest = RNS.Destination(
        identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        "playground",
        "setup",
        "test",
    )
    print(f"  Destination hash : {RNS.prettyhexrep(dest.hash)}")
    print()

    print("All good. Environment is ready.")
    print()
    print("Next steps:")
    print("  pixi run rnsd -v              # start the RNS daemon")
    print("  pixi run rnstatus             # see interface status")
    print("  See experiments/01_hello_rns/ for the first experiment")


if __name__ == "__main__":
    main()
