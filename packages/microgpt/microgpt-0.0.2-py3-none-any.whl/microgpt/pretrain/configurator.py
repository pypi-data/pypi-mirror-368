# configurator.py - imports configuration from config.py
# This file is used by clm_pretrain_v0.py to load configuration overrides

import os
import sys

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'config.py')

# Also try relative path from current working directory
if not os.path.exists(config_path):
    config_path = 'config.py'

# Import the config file
if os.path.exists(config_path):
    # Add the script directory to Python path temporarily
    sys.path.insert(0, script_dir)
    
    # Read and execute the config file to get the variables
    with open(config_path, 'r') as f:
        config_content = f.read()
    
    # Execute the config content in the current globals
    exec(config_content, globals())
    
    # Remove the temporary path
    sys.path.pop(0)
    
    print(f"Configuration loaded from {config_path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {script_dir}")
else:
    print(f"Config file not found at {config_path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {script_dir}")
