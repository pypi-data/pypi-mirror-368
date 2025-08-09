#!/usr/bin/env python3

# Copyright (c) 2025 Muhammed Shafin P (hejhdiss)
# All rights reserved.

import subprocess

def install_sdkman():
    try:
        subprocess.run(
            'curl -s "https://get.sdkman.io" | bash',
            shell=True,
            check=True
        )
        print("✅ SDKMAN installed successfully.")
        print("🔁 Please restart your shell or run:\n   source \"$HOME/.sdkman/bin/sdkman-init.sh\"")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install SDKMAN.")
        print("Error:", e)
        return False

