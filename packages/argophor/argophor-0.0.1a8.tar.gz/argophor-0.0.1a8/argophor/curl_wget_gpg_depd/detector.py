#!/usr/bin/env python3

# Copyright (c) 2025 Muhammed Shafin P (hejhdiss)
# All rights reserved.

import os
import subprocess
import shutil

def is_curl_installed():
    # Method 1: Check if 'curl' is in PATH
    curl_path = shutil.which("curl")
    method_which = curl_path is not None

    # Method 2: Try running 'curl --version'
    try:
        result = subprocess.run(
            ["curl", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        method_version = result.returncode == 0
    except Exception:
        method_version = False

    # Method 3: Check if binary is executable
    method_executable = os.access(curl_path, os.X_OK) if curl_path else False

    return method_which or method_version or method_executable


def is_wget_installed():
    # Method 1: Check if 'wget' is in PATH
    wget_path = shutil.which("wget")
    method_which = wget_path is not None

    # Method 2: Try running 'wget --version'
    try:
        result = subprocess.run(
            ["wget", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        method_version = result.returncode == 0
    except Exception:
        method_version = False

    # Method 3: Check if binary is executable
    method_executable = os.access(wget_path, os.X_OK) if wget_path else False

    return method_which or method_version or method_executable
def is_gpg_installed():
    # Check for gpg or gpg2 in PATH
    gpg_path = shutil.which("gpg") or shutil.which("gpg2")
    method_which = gpg_path is not None

    # Try running 'gpg --version'
    try:
        result = subprocess.run(
            [gpg_path or "gpg", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        method_version = result.returncode == 0
    except Exception:
        method_version = False

    # Check if the binary is executable
    method_executable = os.access(gpg_path, os.X_OK) if gpg_path else False
    return method_which or method_version or method_executable


