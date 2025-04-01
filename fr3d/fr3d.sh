#!/usr/bin/env python3

import os
import sys

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory
parent_dir = os.path.dirname(script_dir)
# Add the parent directory to the Python path
sys.path.insert(0, parent_dir)

# Import the main module
from tool_runner import main

if __name__ == "__main__":
    main()
