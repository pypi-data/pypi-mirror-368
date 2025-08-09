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
import depresolver

def detect():
    if detector.is_sdkman_installed():
        return True
    else:
        return False



# sdkman dectector.py - This file contains methods to detect if SDKMAN is installed.
# It checks various conditions to determine
# If any of this method returns True, then SDKMAN is considered installed.
# Methods:
# Method 1: Check if 'sdk' is in PATH
# Method 2: Try running 'sdk version'
# Method 3: Check if SDKMAN directory exists
# Method 4: Check if sdk script is executable (from previous found)
# Method 5: Check environment variable(checks valid)

def install():
    return installer.install_sdkman()

# sdkman installer.py - This file contains methods to install SDKMAN.
# It uses subprocess to run the installation command.
# It uses curl to download and execute the installation script.
# It returns True if installation is successful, otherwise False.

# Even though it return false or True - Must check, is it correct using detector.py after installation.


def depresolve(password):
    return depresolver.install_dependencies(password)

# sdkman depresolver.py - This file contains methods to resolve dependencies.
# It install curl,zip,unzip,bash which is required by SDKMAN.
# It uses the system's package manager to install these dependencies.
# It checks is it already installed but only uses the shutil.which method.
# It wants user password to run sudo commands.(due to it needs sudo privileges to install packages)