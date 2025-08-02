#!/bin/bash

# Nightly job script that runs NFL data collection and projections
# This script ensures each job completes before starting the next one

echo "$(date): Starting nightly NFL data jobs..."

# Change to the app directory
cd /app

# Run nfl_verse.py first and wait for completion
echo "$(date): Running nfl_verse.py..."
python nfl_stats/nfl_verse.py
if [ $? -eq 0 ]; then
    echo "$(date): nfl_verse.py completed successfully"
else
    echo "$(date): ERROR - nfl_verse.py failed with exit code $?"
    exit 1
fi

# Run get_projections.py after nfl_verse.py completes
echo "$(date): Running get_projections.py..."
python get_projections.py
if [ $? -eq 0 ]; then
    echo "$(date): get_projections.py completed successfully"
else
    echo "$(date): ERROR - get_projections.py failed with exit code $?"
    exit 1
fi

echo "$(date): All nightly jobs completed successfully"
