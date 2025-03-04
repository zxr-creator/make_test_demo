# Makefile/ninja benchmarks
1. Using process_mark.py to run make command and mark processes in dependency graph.
The location of the process_mark.py for each benchmark:
- demo_project/process_mark.py
- json-c/json-c-build/process_mark.py
- libpng/process_mark.py
- redis/process_mark.py
- zlib/process_mark.py
2. add logs to show running time of each part in ninja/make.
3. Alternative projects:
- OpenCV https://github.com/opencv/opencv
- Blender https://github.com/blender/blender
- LLVM https://github.com/llvm/llvm-project
- MySQL https://github.com/mysql/mysql-server