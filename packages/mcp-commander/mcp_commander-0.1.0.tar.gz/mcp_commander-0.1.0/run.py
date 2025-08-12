#!/usr/bin/env python3
"""Direct execution script for mcpCommander without installation."""

import sys
from pathlib import Path

# Add src directory to Python path
repo_root = Path(__file__).parent
src_path = repo_root / "src"
sys.path.insert(0, str(src_path))

# Import and run the CLI
from mcpcommander.cli.main import main

if __name__ == "__main__":
    main()
