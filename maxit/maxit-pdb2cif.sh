#!/usr/bin/env python3

import os
import sys
import stat

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory
parent_dir = os.path.dirname(script_dir)
# Add the parent directory to the Python path
sys.path.insert(0, parent_dir)

# Make this script executable
current_file = os.path.abspath(__file__)
current_mode = os.stat(current_file).st_mode
os.chmod(current_file, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

# Import the main module
from tool_runner import main

if __name__ == "__main__":
    main()
