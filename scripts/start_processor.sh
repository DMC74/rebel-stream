#!/bin/bash

# Source conda
source "$(conda info --base)/etc/profile.d/conda.sh"

# Activate environment
conda activate rebel-stream

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Start the processor
echo "Starting Rebel Stream processor..."
python src/file_watcher.py