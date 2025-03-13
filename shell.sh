#!/bin/bash

# 定义输出文件路径
OUTPUT_FILE="/home/ubuntu/Xinrui/makefile_ninja_benchmarks/pytorch/build/default_output.txt"

# 创建或清空初始 output.txt 文件
> "$OUTPUT_FILE"
cd /home/ubuntu/Xinrui/makefile_ninja_benchmarks/pytorch/build/build_ninja
# 无限循环
while true; do
    # 删除当前目录下所有文件
    cmake -G Ninja ../..
    
    # 运行 ninja 命令并将输出临时存储
    /home/ubuntu/Xinrui/makefile_ninja_benchmarks/ninja_test/ninja > temp_output.txt
    
    # 提取“总耗时:”之后的所有内容并追加到 output.txt
    grep "总耗时" temp_output.txt | sed 's/.*总耗时://' >> "$OUTPUT_FILE"
    
    # 添加时间戳以便追踪每次运行
    echo "Run completed at: $(date)" >> "$OUTPUT_FILE"
    
    # 添加分隔符便于阅读
    echo "----------------" >> "$OUTPUT_FILE"
    
    # 清理临时文件
    setopt rmstarsilent
    rm -rf *
    
    # 短暂休眠避免系统过载
    sleep 1
done