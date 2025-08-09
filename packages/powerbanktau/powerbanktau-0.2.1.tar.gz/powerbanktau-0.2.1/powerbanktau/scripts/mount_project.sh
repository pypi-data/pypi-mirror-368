#!/bin/bash

# Check if the current directory is empty
if [ -z "$(ls -A .)" ]; then
    echo "The current directory is empty. Creating directories..."

    # Create directories
    mkdir -p data scripts notebooks tools gpu_notes

    echo "Directories created: data, scripts, notebooks, tools, notes"
else
    echo "The current directory is not empty. No directories created."
fi