#!/bin/bash

# Check if project path is provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <project_path> <make_path>"
    exit 1
fi

PROJECT_PATH="$1"
MAKE_PATH="$2"

PROJECT_PATH="/home/ubuntu/Xinrui/makefile_ninja_benchmarks/json-c"
MAKE_PATH="/home/ubuntu/Xinrui/makefile_ninja_benchmarks/make_new/make"

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

# Make clean first
make clean
# Run make and append output to log file
"$MAKE_PATH" -j $(nproc) -l $(nproc) 2>&1 | tee -a "$LOG_FILE"

# Step 2: Analyze build log

# Extract make total time from log (assuming make logs "Total time" in microseconds)
# Note: You might need to adjust this grep based on actual Make output format
MAKE_TOTAL_TIME=$(grep "总耗时:" "$LOG_FILE" | awk '{print $3}' | grep -oE '[0-9]+(\.[0-9]+)?' || echo "0")
echo "MAKE_TOTAL_TIME: $MAKE_TOTAL_TIME"
# Convert cmake time to microseconds
CMAKE_TIME_US=$(echo "$CMAKE_TIME * 1000000" | bc)
echo "CMAKE_TIME_US: $CMAKE_TIME_US"
# Calculate total time (cmake + make)
TOTAL_TIME=$(echo "$CMAKE_TIME_US + $MAKE_TOTAL_TIME" | bc)
echo "TOTAL_TIME: $TOTAL_TIME"
# Calculate cmake and make percentages
CMAKE_RATIO=$(echo "$CMAKE_TIME_US / $TOTAL_TIME * 100" | bc -l | awk '{printf "%.2f\n", $0}')
MAKE_RATIO=$(echo "$MAKE_TOTAL_TIME / $TOTAL_TIME * 100" | bc -l | awk '{printf "%.2f\n", $0}')
echo "CMAKE_RATIO: $CMAKE_RATIO"
echo "MAKE_RATIO: $MAKE_RATIO"
# Extract Level 0 timings from log and calculate global percentages
# Note: These may need adjustment based on Make's actual log output
RUN_BUILD_TIME=$(grep "Run Build:" "$LOG_FILE" | awk '{print $4}' || echo "0")
MANIFEST_TIME=$(grep "Argument Parsing and Makefile Updates:" "$LOG_FILE" | awk '{print $7}' || echo "0")
INIT_TIME=$(awk '/[[:space:]]*Initialization:/ {print $3; exit}' "$LOG_FILE")
echo "RUN_BUILD_TIME: $RUN_BUILD_TIME"
echo "MANIFEST_TIME: $MANIFEST_TIME"
echo "INIT_TIME: $INIT_TIME"

# Calculate global percentages for Level 0 stages
RUN_BUILD_RATIO=$(awk "BEGIN {printf \"%.2f\", $RUN_BUILD_TIME/$TOTAL_TIME*100}")
MANIFEST_RATIO=$(awk "BEGIN {printf \"%.2f\", $MANIFEST_TIME/$TOTAL_TIME*100}")
INIT_RATIO=$(awk "BEGIN {printf \"%.2f\", $INIT_TIME/$TOTAL_TIME*100}")
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
    echo "  Argument Parsing and Makefile Updates: $MANIFEST_TIME microseconds ($MANIFEST_RATIO%)"
    echo "  Initialization: $INIT_TIME microseconds ($INIT_RATIO%)"
} >> "$LOG_FILE"

# Step 3: Generate dependency graphs
"$MAKE_PATH" -Bnd | make2graph > "$GRAPH_DOT"

# Return to root directory
cd ..
cd ..