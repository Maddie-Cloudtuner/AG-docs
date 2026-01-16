#!/usr/bin/env bash

# Get the directory where the script is located and move to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.." || exit 1

# Run the development multi-runner
python3 -m runners.dev_host_runner_multi
