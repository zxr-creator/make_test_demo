# Makefile/ninja benchmarks
1. Using process_mark.py to run make command and mark processes in dependency graph.
The location of the process_mark.py for each benchmark:
- demo_project/process_mark.py
- json-c/json-c-build/process_mark.py
- libpng/process_mark.py
- redis/process_mark.py
- zlib/process_mark.py
2. Add logs to show running time of each part in ninja/make.

3. Compile with custom make and try it on the benchmarks(take libpng as an example)
The first thing to do is to add the C++ compiler and flags to the Makefile. Remember to add the C++ compiler and flags to the Makefile every time you delete the Makefile and after you run ./configure (like running the command make distclean).

- Step 1: Add C++ Compiler and Flags
You need to define the C++ compiler (CXX) and its flags (CXXFLAGS) in the Makefile. Since this is an Automake-generated Makefile, place these definitions near the top, alongside similar variables like CC and CFLAGS, to maintain consistency.

Where to Add: After the existing compiler definitions around line 600-620, where CC, CFLAGS, and related variables are defined.
What to Add:

CXX = g++
CXXFLAGS = -std=c++14

This specifies g++ as the C++ compiler and sets the C++11 standard, which is a reasonable default for modern C++ code unless your timetracker.cpp requires a different standard (e.g., C++17 or C++20).

- Step 2: Add Compilation Rule for timetracker.o
Since timetracker.cpp and timetracker.h are likely in the src/ directory (consistent with other source files in this Makefile), you need a rule to compile timetracker.cpp into src/timetracker.o. This rule should use the C++ compiler and include necessary preprocessor flags from the existing build system.

Where to Add: After the existing object file rules, before the make$(EXEEXT) target definition. This keeps it with other compilation rules.
What to Add:
src/profiler.o: src/profiler.cpp src/profiler.h
	$(CXX) $(CXXFLAGS) $(AM_CPPFLAGS) $(CPPFLAGS) -c src/profiler.cpp -o src/profiler.o

- Step 3: Update the Object List
The make executable is built from the objects listed in make_OBJECTS, which is derived from am_make_OBJECTS. The am__objects_1 variable contains the object files from make_SRCS, which includes most of the core source files. You need to add src/profiler.o to this list.

Where to Find: Search for am__objects_1 =.

am__objects_1 = src/ar.$(OBJEXT) src/arscan.$(OBJEXT) src/commands.$(OBJEXT) ...
What to Modify: Append src/timetracker.o to the end of am__objects_1. Since $(OBJEXT) is defined as o in this Makefile, use src/profiler.o.
Modified Line (partial excerpt):

am__objects_1 = src/ar.o src/arscan.o src/commands.o ... src/profiler.$(OBJEXT)

Explanation:
Adding src/timetracker.o ensures it’s included in am_make_OBJECTS, which feeds into make_OBJECTS.
The $(OBJEXT) substitution is already handled by Automake, but since it’s o, you can write it directly as .o.
Step 4: Update the Linking Rule
Since timetracker.o is a C++ object file, the final linking step must use the C++ compiler (g++) instead of the C compiler (gcc) to correctly link C++ standard libraries and handle any C++-specific requirements. The linking command is defined by the LINK variable.

Where to Find: Search for LINK = around line 620-630, just after CCLD = $(CC).
Original Line:

LINK = $(CCLD) $(AM_CFLAGS) $(CFLAGS) $(AM_LDFLAGS) $(LDFLAGS) -o $@

What to Modify: Replace it to use $(CXX) and remove C-specific flags that aren’t needed for linking, relying on linker flags instead.
Modified Line:

LINK = $(CXX) $(AM_LDFLAGS) $(LDFLAGS) -o $@

- cd ./make_new
- make clean
- make
- cd ../libpng
- /home/ubuntu/Xinrui/makefile_ninja_benchmarks/make_new/make clean
- sudo /home/ubuntu/Xinrui/makefile_ninja_benchmarks/make_new/make -d > make_profile.txt
or
- cd ./make_new
- make clean
- make
- cd ..
- sh launch_make.sh /home/ubuntu/Xinrui/makefile_ninja_benchmarks/json-c /home/ubuntu/Xinrui/makefile_ninja_benchmarks/make_new/make

4. Compile with custom ninja
- python configure.py --bootstrap
- cd ..
- sh launch_ninja.sh /home/ubuntu/Xinrui/makefile_ninja_benchmarks/json-c /home/ubuntu/Xinrui/makefile_ninja_benchmarks/ninja_test/ninja

5. Compile Pytorch with Make and Ninja
- source pytorch-build-env/bin/activate
- pip install --upgrade pip setuptools
- git clone --recursive https://github.com/pytorch/pytorch.git
- cd pytorch
- export CUDA_HOME=/usr/local/cuda-12.4
- export PATH="$CUDA_HOME/bin:${PATH}"
- export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH}"
- git checkout v2.6.0
- git submodule sync && git submodule update --init --recursive
sh launch_make_pytorch.sh /home/ubuntu/Xinrui/makefile_ninja_benchmarks/pytorch /home/ubuntu/Xinrui/makefile_ninja_benchmarks/make_new/make
sh launch_ninja_pytorch.sh /home/ubuntu/Xinrui/makefile_ninja_benchmarks/pytorch /home/ubuntu/Xinrui/makefile_ninja_benchmarks/ninja_test/ninja

sh launch_make.sh /home/ubuntu/Xinrui/makefile_ninja_benchmarks/opencv /home/ubuntu/Xinrui/makefile_ninja_benchmarks/make_new/make
sh launch_ninja.sh /home/ubuntu/Xinrui/makefile_ninja_benchmarks/opencv /home/ubuntu/Xinrui/makefile_ninja_benchmarks/ninja_test/ninja
6. Alternative projects:
- OpenCV https://github.com/opencv/opencv
- Blender https://github.com/blender/blender
- LLVM https://github.com/llvm/llvm-project
- MySQL https://github.com/mysql/mysql-server
- Catalyst https://github.com/catalyst-team/catalyst
