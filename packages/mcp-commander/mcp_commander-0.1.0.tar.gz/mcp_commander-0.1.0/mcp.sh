#!/bin/bash
# Shell wrapper for mcpCommander direct execution

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to include src directory
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# Execute the CLI
python -m mcpcommander "$@"
