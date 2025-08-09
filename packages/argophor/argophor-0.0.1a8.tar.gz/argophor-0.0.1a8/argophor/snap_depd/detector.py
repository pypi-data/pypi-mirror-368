#!/usr/bin/env python3

# Copyright (c) 2025 Muhammed Shafin P (hejhdiss)
# All rights reserved.

import subprocess
import shutil
import os

def is_snapd_installed():
    # Method 1: Check if snap command is available
    method_which = shutil.which("snap") is not None

    # Method 2: Try running 'snap version'
    try:
        method_version = subprocess.run(
            ["snap", "version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        ).returncode == 0
    except Exception:
        method_version = False

    # Method 3: Check for snapd service file (systemd based)
    method_service = os.path.exists("/lib/systemd/system/snapd.service") or \
                     os.path.exists("/etc/systemd/system/snapd.service")

    return method_which or method_version or method_service


def is_snap_app_installed(app_name):
    if not is_snapd_installed():
        return False

    try:
        result = subprocess.run(
            ["snap", "list"],
            check=True,
            capture_output=True,
            text=True
        )
        return app_name.lower() in result.stdout.lower()
    except Exception:
        return False
    

def check_snapd():
    if is_snapd_installed():
        print("✅ snapd is installed and working.")
        return True
    else:
        print("❌ snapd is not available.")
        return False

def check_snap_store():
    if is_snap_app_installed("snap-store"):
        print("✅ snap-store is installed via Snap.")
        return True
    else:
        print("❌ snap-store is not installed via Snap.")
        return False

