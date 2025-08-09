#!/usr/bin/env python3

# Copyright (c) 2025 Muhammed Shafin P (hejhdiss)
# All rights reserved.

import os
import subprocess
import shutil

def is_sdkman_installed():
    # Method 1: Check if 'sdk' is in PATH
    sdk_in_path = shutil.which("sdk") is not None

    # Method 2: Try running 'sdk version'
    try:
        result = subprocess.run(
            ["sdk", "version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        sdk_version_works = result.returncode == 0
    except Exception:
        sdk_version_works = False

    # Method 3: Check if SDKMAN directory exists
    sdkman_dir = os.path.expanduser("~/.sdkman")
    sdkman_dir_exists = os.path.isdir(sdkman_dir)

    # Method 4: Check if sdk script is executable
    sdk_script_path = os.path.join(sdkman_dir, "bin", "sdk")
    sdk_script_executable = os.path.isfile(sdk_script_path) and os.access(sdk_script_path, os.X_OK)

    # Method 5: Check environment variable
    sdkman_env_var = "SDKMAN_DIR" in os.environ
    sdkman_env_path = os.environ.get("SDKMAN_DIR", "")
    sdkman_env_valid = os.path.isfile(os.path.join(sdkman_env_path, "bin", "sdk")) if sdkman_env_var else False

    # Final result: return True if any method worked
    return any([
        sdk_in_path,
        sdk_version_works,
        sdkman_dir_exists,
        sdk_script_executable,
        sdkman_env_valid
    ])
