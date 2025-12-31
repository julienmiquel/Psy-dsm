#!/bin/bash

# Check arguments
if [ "$1" == "podcasts" ]; then
    TARGET_FOLDER="$2"
    
    if [ ! -d "$TARGET_FOLDER" ]; then
        echo "Error: Target folder $TARGET_FOLDER does not exist."
        exit 1
    fi

    echo "========================================"
    echo "Running batch generation on:"
    echo "$TARGET_FOLDER"
    echo "========================================"
    
    export PYTHONPATH=.
    
    if [ -d ".venv" ]; then
        echo "Using .venv..."
        source .venv/bin/activate
        # Ensure dependencies are installed in the venv
        poetry install
        python src/batch_runner.py generate "$TARGET_FOLDER"
    else
        echo "Using poetry..."
        poetry install
        poetry run python src/batch_runner.py generate "$TARGET_FOLDER"
    fi
    
    echo "========================================"
    echo "Verifying Output in Input Folder..."
    echo "========================================"
    
    sleepcasts=$(find "$TARGET_FOLDER" -name "audio_sleepcast_mixed_*.wav" | wc -l)
    podcasts=$(find "$TARGET_FOLDER" -name "audio_module_*.wav" | wc -l)
    full_podcast=$(find "$TARGET_FOLDER" -name "audio_full.wav" | wc -l)
    
    echo "Sleepcasts (Mixed): $sleepcasts"
    echo "Module Podcasts:    $podcasts"
    echo "Full Podcast:       $full_podcast"
    
    echo "Done."
else
    echo "Usage: ./run.sh podcasts <target_folder>"
fi
