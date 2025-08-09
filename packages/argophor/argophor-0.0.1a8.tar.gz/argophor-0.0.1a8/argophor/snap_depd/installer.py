#!/usr/bin/env python3

# Copyright (c) 2025 Muhammed Shafin P (hejhdiss)
# All rights reserved.

import subprocess
import shutil
import sys
import os

def get_package_manager():
    for pm in ["apt", "dnf", "yum", "pacman", "zypper"]:
        if shutil.which(pm):
            return pm
    return None

def run_sudo_command(command, password):
    try:
        result = subprocess.run(
            ["sudo", "-S"] + command,
            input=password + "\n",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception:
        return False

def post_install_snapd(password):
    """Enable snapd service and fix /snap link if needed."""
    run_sudo_command(["systemctl", "enable", "--now", "snapd.socket"], password)

    # For distros without /snap link
    if not os.path.exists("/snap"):
        run_sudo_command(["ln", "-s", "/var/lib/snapd/snap", "/snap"], password)

    # For openSUSE-specific apparmor unit
    if os.path.exists("/usr/lib/systemd/system/snapd.apparmor.service"):
        run_sudo_command(["systemctl", "enable", "--now", "snapd.apparmor"], password)

def install_package(pkg_name, password):
    pm = get_package_manager()
    if not pm:
        print("❌ No supported package manager found.")
        return False

    print(f"📦 Installing {pkg_name} using {pm}...")

    try:
        if pm == "apt":
            run_sudo_command(["apt", "update"], password)
            success = run_sudo_command(["apt", "install", "-y", pkg_name], password)

        elif pm == "dnf":
            success = run_sudo_command(["dnf", "install", "-y", pkg_name], password)

        elif pm == "yum":
            success = run_sudo_command(["yum", "install", "-y", pkg_name], password)

        elif pm == "pacman":
            success = run_sudo_command(["pacman", "-Sy", pkg_name, "--noconfirm"], password)

        elif pm == "zypper":
            success = run_sudo_command(["zypper", "install", "-y", pkg_name], password)

        else:
            success = False

        # Post-install actions for snapd
        if success and pkg_name == "snapd":
            post_install_snapd(password)

        return success

    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {pkg_name} using {pm}.")
        return False

def install_snapd(password):
    """Install snapd package."""
    if not install_package("snapd", password):
        print("❌ Failed to install snapd.")
        return False

    print("✅ snapd installed successfully.")
    return True

def install_snap_store(password):
    try:
        # Install snap-store
        result = subprocess.run(
            ["sudo", "-S", "snap", "install", "snap-store"],
            input=password + "\n",
            text=True
        )
        if result.returncode == 0:
            print("✅ Snap Store installed successfully.")
            return True
        else:
            print("❌ Failed to install Snap Store.")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False