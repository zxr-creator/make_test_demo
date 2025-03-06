#!/bin/bash

# Check if project path is provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <project_path> <make_path>"
    exit 1
fi

PROJECT_PATH="/home/ubuntu/efs/Xinrui/makefile_ninja_benchmarks/libpng"
MAKE_PATH="/home/ubuntu/efs/Xinrui/makefile_ninja_benchmarks/make_new/make"

# Change to project directory
cd "$PROJECT_PATH" || {
    echo "Error: Could not change to directory '$PROJECT_PATH'"
    exit 1
}

# Define file names
LOG_FILE="build_log.txt"
GRAPH_DOT="graph.dot"
GRAPH_SVG="graph.svg"

# Step 1: Clean up previous build and Launch build

# Remove and recreate build directory
rm -rf build_make
mkdir -p build_make
cd build_make

# 使用 /usr/bin/time -p 来捕获 cmake 的执行时间
CMAKE_OUTPUT=$( { /usr/bin/time -p cmake .. 2>&1 | tee /dev/tty; } )

# 使用 grep 提取以 "real" 开头的行，并用 awk 取出时间数值
CMAKE_TIME=$(echo "$CMAKE_OUTPUT" | grep '^real' | awk '{print $2}')

# Run make and append output to log file
"$MAKE_PATH" -j$(nproc) -l$(nproc) 2>&1 | tee -a "$LOG_FILE"

# Step 2: Analyze build log

# Extract make total time from log (in microseconds)
MAKE_TOTAL_TIME=$(grep "总耗时:" "$LOG_FILE" | tail -n 1 | awk -F: '{print $2}' | grep -o '[0-9]*' || echo "0")

# Convert cmake time to microseconds
CMAKE_TIME_US=$(echo "$CMAKE_TIME * 1000000" | bc)

# Calculate total time (cmake + make)
TOTAL_TIME=$(echo "$CMAKE_TIME_US + $MAKE_TOTAL_TIME" | bc)

# Calculate cmake and make percentages
CMAKE_RATIO=$(echo "scale=2; $CMAKE_TIME_US / $TOTAL_TIME * 100" | bc)
MAKE_RATIO=$(echo "scale=2; $MAKE_TOTAL_TIME / $TOTAL_TIME * 100" | bc)

# Extract Level 0 timings from log and calculate global percentages
RUN_BUILD_TIME=$(grep "Run Build:" "$LOG_FILE" | tail -n 1 | awk -F: '{print $2}' | grep -o '[0-9]*' | head -n 1 || echo "0")
MANIFEST_TIME=$(grep "Manifest Parsing and Rebuilding:" "$LOG_FILE" | tail -n 1 | awk '{for (i=1; i<=NF; i++) if ($i ~ /^[0-9]+$/) {print $i; exit}}' || echo "0")
INIT_TIME=$(grep "[[:space:]]*Initialization:" "$LOG_FILE" | tail -n 1 | awk -F: '{print $2}' | grep -o '[0-9]*' | head -n 1 || echo "0")

# Calculate global percentages for Level 0 stages
RUN_BUILD_RATIO=$(echo "scale=2; $RUN_BUILD_TIME / $TOTAL_TIME * 100" | bc)
MANIFEST_RATIO=$(echo "scale=2; $MANIFEST_TIME / $TOTAL_TIME * 100" | bc)
INIT_RATIO=$(echo "scale=2; $INIT_TIME / $TOTAL_TIME * 100" | bc)

# Append results to log file
{
    echo "--------------------------------------------------"
    echo "CMake time: $CMAKE_TIME_US microseconds"
    echo "Make total time: $MAKE_TOTAL_TIME microseconds"
    echo "Total time: $TOTAL_TIME microseconds"
    echo "CMake ratio: $CMAKE_RATIO%"
    echo "Make ratio: $MAKE_RATIO%"
    echo "Level 0 Global Percentages:"
    echo "  Run Build: $RUN_BUILD_TIME microseconds ($RUN_BUILD_RATIO%)"
    echo "  Manifest Parsing and Rebuilding: $MANIFEST_TIME microseconds ($MANIFEST_RATIO%)"
    echo "  Initialization: $INIT_TIME microseconds ($INIT_RATIO%)"
} >> "$LOG_FILE"

# Step 3: Generate dependency graphs
"$MAKE_PATH" -Bnd | make2graph > "$GRAPH_DOT"
dot -Tsvg "$GRAPH_DOT" -o "$GRAPH_SVG"

# Return to root directory
cd ..
cd ..