#!/bin/bash

# 硬编码路径参数
PROJECT_PATH="/home/ubuntu/Xinrui/makefile_ninja_benchmarks/pytorch"
MAKE_PATH="/home/ubuntu/Xinrui/makefile_ninja_benchmarks/make_new/make"
NINJA_PATH="/home/ubuntu/Xinrui/makefile_ninja_benchmarks/ninja_test/ninja"
DOT_ANALYSIS_FILE_PATH="/home/ubuntu/Xinrui/makefile_ninja_benchmarks/graph_dot_analysis.py"

rm -rf build

mkdir build
cd build

echo "Running Make build..."
../launch_make.sh "$PROJECT_PATH" "$MAKE_PATH"

echo "Running Ninja build..."
../launch_ninja.sh "$PROJECT_PATH" "$NINJA_PATH"



python "$DOT_ANALYSIS_FILE_PATH" "$PROJECT_PATH"
cd ..
echo "Done"
