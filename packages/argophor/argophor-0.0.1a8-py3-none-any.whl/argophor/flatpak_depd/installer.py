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
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception:
        return False

def install_package(pkg_name, password):
    pm = get_package_manager()
    if not pm:
        print("❌ No supported package manager found (APT, DNF, YUM, PACMAN, ZYPPER).")
        return False

    print(f"📦 Installing {pkg_name} using {pm}...")

    try:
        if pm == "apt":
            run_sudo_command(["apt", "update"], password)
            return run_sudo_command(["apt", "install", "-y", pkg_name], password)

        elif pm == "dnf":
            return run_sudo_command(["dnf", "install", "-y", pkg_name], password)

        elif pm == "yum":
            return run_sudo_command(["yum", "install", "-y", pkg_name], password)

        elif pm == "pacman":
            return run_sudo_command(["pacman", "-Sy", pkg_name, "--noconfirm"], password)

        elif pm == "zypper":
            return run_sudo_command(["zypper", "install", "-y", pkg_name], password)

    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {pkg_name} using {pm}.")
        return False

def install_flatpak(password):
    if not install_package("flatpak", password):
        print("❌ Failed to install Flatpak.")
        return False

    print("✅ Flatpak installed successfully.")
    return True
def add_flathub(password):
    print("➕ Adding Flathub repository...")
    return run_sudo_command([
        "flatpak", "remote-add", "--if-not-exists",
        "flathub", "https://dl.flathub.org/repo/flathub.flatpakrepo"
    ], password)
