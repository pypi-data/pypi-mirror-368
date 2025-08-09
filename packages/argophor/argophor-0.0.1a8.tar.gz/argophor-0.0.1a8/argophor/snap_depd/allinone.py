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
    return detector.check_snapd()

def detect_store():
    return detector.check_snap_store()

# snap dectector.py - This file contains methods to detect if snapd is installed.
# It checks various conditions to determine 
# If any of this method returns True, then snapd is considered installed.
# Methods:  
# Method 1: Check if snap command is available
# Method 2: Try running 'snap version'          
# Method 3: Check for snapd service file (systemd based)

# It also checks snap-store app is installed via Snap.
# It inside check is snap installed as per above said methods.

def install(password):
    return installer.install_snapd(password)

def install_store(password):
    return installer.install_snap_store(password)

# snap installer.py - This file contains methods to install snapd.
# It uses subprocess to run the installation command.   
# It uses the system's package manager to install snapd.
# It returns True if installation is successful, otherwise False.   
# It also installs snap-store app if requested.
# It uses the snap to install snap-store app.
# Better to use detector.py to check if snap-store or snap is installed after installation.
# Also use detector.py to check is snapd presnt or not before snap-store installation.
# It have some post-installation steps like enabling snapd service and creating /snap link if needed.