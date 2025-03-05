#!/bin/bash

# Check if project path is provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <project_path> <ninja_path>"
    exit 1
fi

PROJECT_PATH="$1"
NINJA_PATH="$2"

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
rm -rf build_ninja
mkdir -p build_ninja
cd build_ninja

# Run cmake and measure precise time
# Using `time` command directly and capturing its output
CMAKE_OUTPUT=$( { /usr/bin/time -p cmake .. 2>&1 | tee /dev/tty; } )

# 使用 grep 提取以 "real" 开头的行，并用 awk 取出时间数值
CMAKE_TIME=$(echo "$CMAKE_OUTPUT" | grep '^real' | awk '{print $2}')

echo $CMAKE_TIME
# Run ninja and append output to log file
"$NINJA_PATH" 2>&1 | tee -a "$LOG_FILE"

# Step 2: Analyze build log

# Extract ninja total time from log (assuming ninja logs "Total time" in microseconds)
# Note: You might need to adjust this grep based on actual Ninja output format
NINJA_TOTAL_TIME=$(grep "总耗时:" "$LOG_FILE" | awk '{print $2}' || echo "0")

# Convert cmake time to microseconds
CMAKE_TIME_US=$(echo "$CMAKE_TIME * 1000000" | bc)

# Calculate total time (cmake + ninja)
TOTAL_TIME=$(echo "$CMAKE_TIME_US + $NINJA_TOTAL_TIME" | bc)

# Calculate cmake and ninja percentages
CMAKE_RATIO=$(echo "scale=2; $CMAKE_TIME_US / $TOTAL_TIME * 100" | bc)
NINJA_RATIO=$(echo "scale=2; $NINJA_TOTAL_TIME / $TOTAL_TIME * 100" | bc)

# Extract Level 0 timings from log and calculate global percentages
# Note: These may need adjustment based on Ninja's actual log output
RUN_BUILD_TIME=$(grep "Run Build:" "$LOG_FILE" | awk '{print $3}' || echo "0")
MANIFEST_TIME=$(grep "Manifest Parsing and Rebuilding:" "$LOG_FILE" | awk '{print $5}' || echo "0")
INIT_TIME=$(awk '/[[:space:]]*Initialization:/ {print $2; exit}' "$LOG_FILE")

# Calculate global percentages for Level 0 stages
RUN_BUILD_RATIO=$(echo "scale=2; $RUN_BUILD_TIME / $TOTAL_TIME * 100" | bc)
MANIFEST_RATIO=$(echo "scale=2; $MANIFEST_TIME / $TOTAL_TIME * 100" | bc)
INIT_RATIO=$(echo "scale=2; $INIT_TIME / $TOTAL_TIME * 100" | bc)

# Append results to log file
{
    echo "--------------------------------------------------"
    echo "CMake time: $CMAKE_TIME_US microseconds"
    echo "Ninja total time: $NINJA_TOTAL_TIME microseconds"
    echo "Total time: $TOTAL_TIME microseconds"
    echo "CMake ratio: $CMAKE_RATIO%"
    echo "Ninja ratio: $NINJA_RATIO%"
    echo "Level 0 Global Percentages:"
    echo "  Run Build: $RUN_BUILD_TIME microseconds ($RUN_BUILD_RATIO%)"
    echo "  Manifest Parsing and Rebuilding: $MANIFEST_TIME microseconds ($MANIFEST_RATIO%)"
    echo "  Initialization: $INIT_TIME microseconds ($INIT_RATIO%)"
} >> "$LOG_FILE"

# Step 3: Generate dependency graph using ninja
"$NINJA_PATH" -t graph > "$GRAPH_DOT"
dot -Tsvg "$GRAPH_DOT" -o "$GRAPH_SVG"

# Return to root directory
cd ..