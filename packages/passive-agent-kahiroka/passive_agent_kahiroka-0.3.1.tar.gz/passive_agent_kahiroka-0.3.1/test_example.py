#!/usr/bin/env python3
"""
Test script that runs passive-agent in the example directory.
"""

import os
import sys
import subprocess

def main():
    # Save current directory
    original_dir = os.getcwd()
    
    # Change to example directory
    example_dir = os.path.join(original_dir, 'example')
    if not os.path.exists(example_dir):
        print(f"Error: Example directory not found at {example_dir}")
        sys.exit(1)
    
    try:
        os.chdir(example_dir)
        print(f"Changed to directory: {os.getcwd()}")
        print("=" * 50)
        
        # Add the src directory to Python path so we can import the package
        src_path = os.path.join(original_dir, 'src')
        sys.path.insert(0, src_path)
        
        # Import and run the main function directly
        from passive_agent import main
        main()
        
    finally:
        # Change back to original directory
        os.chdir(original_dir)

if __name__ == '__main__':
    main()