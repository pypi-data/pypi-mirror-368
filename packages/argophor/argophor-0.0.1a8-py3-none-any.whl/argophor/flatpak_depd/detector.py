#!/usr/bin/env python3

# Copyright (c) 2025 Muhammed Shafin P (hejhdiss)
# All rights reserved.

import subprocess
import shutil
import os

def is_flatpak_installed():
    method_which = shutil.which("flatpak") is not None

    try:
        method_version = subprocess.run(
            ["flatpak", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        ).returncode == 0
    except Exception:
        method_version = False

    flatpak_path = shutil.which("flatpak")
    method_executable = os.access(flatpak_path, os.X_OK) if flatpak_path else False

    # Final result: true if any method is true
    return method_which or method_version or method_executable


def is_flathub_added():
    if not is_flatpak_installed():
        return False

    # Method 1: check via `flatpak remotes`
    try:
        result = subprocess.run(
            ["flatpak", "remotes"],
            check=True,
            capture_output=True,
            text=True
        )
        method_remote = "flathub" in result.stdout.lower()
    except Exception:
        method_remote = False

    # Method 2: check via known repo file paths
    known_paths = [
        "/etc/flatpak/remotes.d/flathub.flatpakrepo",
        "/var/lib/flatpak/repo/flathub",
        os.path.expanduser("~/.local/share/flatpak/repo/flathub")
    ]
    method_path_exists = any(os.path.exists(p) for p in known_paths)

    # Final result: true if any method is true
    return method_remote or method_path_exists

