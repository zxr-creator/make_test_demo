# Makefile/ninja benchmarks
1. Using process_mark.py to run make command and mark processes in dependency graph.
The location of the process_mark.py for each benchmark:
- demo_project/process_mark.py
- json-c/json-c-build/process_mark.py
- libpng/process_mark.py
- redis/process_mark.py
- zlib/process_mark.py
2. Add logs to show running time of each part in ninja/make.

3. Compile the custom make and try it on the benchmarks(take libpng as an example)
- cd ./make_new
- make clean
- make
- cd ../libpng
- /home/ued520/makefile_ninja_benchmarks/make_new/make clean
- sudo /home/ued520/makefile_ninja_benchmarks/make_new/make -d > make_profile.txt

4. Compile the custom ninja (to be add)


5. Alternative projects:
- OpenCV https://github.com/opencv/opencv
- Blender https://github.com/blender/blender
- LLVM https://github.com/llvm/llvm-project
- MySQL https://github.com/mysql/mysql-server
