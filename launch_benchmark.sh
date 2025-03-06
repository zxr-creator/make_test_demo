#!/bin/bash

# 硬编码路径参数
PROJECT_PATH="/scorpio/home/shenao/myProject/makefile_ninja_benchmarks/ninja_test/simplest_project"
MAKE_PATH="/scorpio/home/shenao/myProject/makefile_ninja_benchmarks/ninja_test/make"
NINJA_PATH="/scorpio/home/shenao/myProject/makefile_ninja_benchmarks/ninja_test/ninja"

echo "Running Make build..."
./launch_make.sh "$PROJECT_PATH" "$MAKE_PATH"

echo "Running Ninja build..."
./launch_ninja.sh "$PROJECT_PATH" "$NINJA_PATH"

echo "Done"
