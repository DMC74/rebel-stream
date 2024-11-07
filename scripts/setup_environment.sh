#!/bin/bash

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda is not installed or not in PATH"
    exit 1
fi

# Set environment name
ENV_NAME="rebel-stream"

# Create new conda environment if it doesn't exist
if ! conda env list | grep -q "^$ENV_NAME "; then
    echo "Creating new conda environment: $ENV_NAME"
    conda create -n $ENV_NAME python=3.10 -y
else
    echo "Environment $ENV_NAME already exists"
fi

# Activate environment and install requirements
echo "Activating environment and installing requirements..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME

# Install PyTorch with CPU support (modify for GPU if needed)
conda install pytorch cpuonly -c pytorch -y

# Install other requirements
pip install -r requirements.txt

# Create necessary directories
mkdir -p data/input_documents data/processed_documents data/archived_documents

echo "Setup complete! You can now run: ./scripts/start_processor.sh"