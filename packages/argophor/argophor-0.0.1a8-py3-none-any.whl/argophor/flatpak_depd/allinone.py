#!/usr/bin/env python3

# Copyright (c) 2025 Muhammed Shafin P (hejhdiss)
# All rights reserved.

import subprocess
import shutil
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import detector
import installer 

def detect():
    if detector.is_flatpak_installed():
        print("✅ Flatpak is already installed.")
        return True
    else:
        print("❌ Flatpak is not installed.")
        return False
def detect_flathub():
    if detector.is_flathub_added():
        print("✅ Flathub is already added.")
        return True
    else:
        print("❌ Flathub is not added.")
        return False

# flatpak detector.py - This file contains methods to detect if flatpak is installed.
# It checks various conditions to determine
# If any of this method returns True, then flatpak is considered installed.
# Methods:
# Method 1: Check if 'flatpak' is in PATH   
# Method 2: Try running 'flatpak --version'
# Method 3: Check if flatpak executable is accessible and executable

# It also supports to check is flathub added or not.
# It checks via `flatpak remotes` command and known repo file paths.
# If any of this method returns True, then flathub is considered added.

def install(password):
    return installer.install_flatpak(password)

def install_flathub(password):
    return installer.install_flathub(password)

# flatpak installer.py - This file contains methods to install flatpak.
# It uses subprocess to run the installation command.   
# It uses the system's package manager to install flatpak.
# It returns True if installation is successful, otherwise False.
# It also supports to install flathub repository.
# It uses the system's package manager to install flathub.
# It returns True if installation is successful, otherwise False.
# Even though it return false or True - Must check, is it correct using detector.py after installation.
# It wants user password to run sudo commands.(due to it needs sudo privileges to install packages)