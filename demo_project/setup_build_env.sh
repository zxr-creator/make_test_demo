#!/bin/bash

# 设置编译器
export CC=/usr/bin/gcc
export CXX=/usr/bin/g++

# 设置 Ninja 构建工具
export CMAKE_MAKE_PROGRAM=/usr/bin/ninja

# 如果你有其他环境变量需求，可以在这里添加

# 运行 CMake 配置
cmake -G Ninja .
