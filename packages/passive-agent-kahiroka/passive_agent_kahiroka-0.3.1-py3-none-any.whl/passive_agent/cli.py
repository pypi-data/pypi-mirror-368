#!/usr/bin/env python3
"""
CLI entry point for passive-agent.
"""

import sys
from .core import main as core_main

def main():
    """CLI entry point."""
    try:
        core_main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()