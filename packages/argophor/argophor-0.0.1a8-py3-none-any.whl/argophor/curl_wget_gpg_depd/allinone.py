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

def detect_curl():
    if detector.is_curl_installed():
        print("✅ curl is already installed.")
        return True
    else:
        print("❌ curl is not installed.")
        return False
def detect_wget():  
    if detector.is_wget_installed():
        print("✅ wget is already installed.")
        return True
    else:
        print("❌ wget is not installed.")
        return False
def detect_gpg():
    if detector.is_gpg_installed():
        print("✅ gpg is already installed.")
        return True
    else:
        print("❌ gpg is not installed.")
        return False

# curl,wget,gpg detector.py - This script detects if curl, wget, and gpg are installed on the system.
# It checks curl, wget, and gpg using multiple methods,if any of the methods succeed, it considers the tool installed.
# Methods:
# 1. Check if the tool is in PATH using shutil.which.
# 2. Try running the tool with a version command (e.g., curl --version)
# 3. Check if the binary is executable using os.access.

def install_curl(password):
    return installer.install_curl_if_missing(password)
 
def install_wget(password):
    return installer.install_wget_if_missing(password)

def install_gpg(password):
    return installer.install_gpg_if_missing(password)

# curl,wget,gpg installer.py - This script installs curl, wget, and gpg using the system's package manager.
# It detects the package manager (APT, DNF, YUM, PACMAN, ZYPPER) and installs the required packages.
# it have basic checking for the package manager and handles errors during installation.
# better to check using detector.py,even if it return True or False.
# Install function of gpg doesnt have basic checking of preinstalled gpg.