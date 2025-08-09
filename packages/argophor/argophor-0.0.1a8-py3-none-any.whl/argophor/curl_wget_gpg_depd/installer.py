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


def install_curl_if_missing(password):
    if shutil.which("curl") is None:
        if install_package("curl", password):
            print("✅ curl installed successfully.")
            return True
        else:
            print("❌ curl installation failed.")
            return False
    print("✅ curl is already installed.")
    return True

def install_wget_if_missing(password):
    if shutil.which("wget") is None:
        if install_package("wget", password):
            print("✅ wget installed successfully.")
            return True
        else:
            print("❌ wget installation failed.")
            return False
    print("✅ wget is already installed.")
    return True

def install_gpg_if_missing(password):
        pkg_name = "gnupg"
        if install_package(pkg_name, password):
            print("✅ GPG (gnupg) installed successfully.")
            return True
        else:
            print("❌ GPG (gnupg) installation failed.")
            return False
