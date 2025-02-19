#!/bin/bash

# Define thread counts to test
THREADS=(2 4 8 16 32 64)

# Loop through different MAX_JOBS values
for t in "${THREADS[@]}"; do
    echo "Building Docker image (no cache)..."
    docker build --no-cache -t pytorch-build .
    
    echo "Running build test with MAX_JOBS=$t"
    docker run --rm -it -e MAX_JOBS=$t pytorch-build > "output${t}.log" 2>&1
done

echo "All tests completed."
