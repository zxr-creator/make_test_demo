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

Where to Add: After the existing object file rules, around line 1500-1600, before the make$(EXEEXT) target definition. This keeps it with other compilation rules.
What to Add:
src/timetracker.o: src/timetracker.cpp src/timetracker.h
	$(CXX) $(CXXFLAGS) $(AM_CPPFLAGS) $(CPPFLAGS) -c src/timetracker.cpp -o src/timetracker.o

Explanation:
src/timetracker.o: src/timetracker.cpp src/timetracker.h specifies the target and its dependencies.
$(CXX) uses the C++ compiler defined earlier (g++).
$(CXXFLAGS) applies the C++ flags (-std=c++11).
$(AM_CPPFLAGS) includes existing include paths (e.g., -Isrc -Ilib), ensuring timetracker.cpp can find headers.
$(CPPFLAGS) allows for additional preprocessor flags if defined.
-c compiles the source file into an object file without linking.
-o src/timetracker.o specifies the output object file.
If timetracker.cpp and timetracker.h are not in src/, adjust the paths accordingly (e.g., timetracker.o: timetracker.cpp timetracker.h if they’re in the root directory).

- Step 3: Update the Object List
The make executable is built from the objects listed in make_OBJECTS, which is derived from am_make_OBJECTS. The am__objects_1 variable contains the object files from make_SRCS, which includes most of the core source files. You need to add src/timetracker.o to this list.

Where to Find: Search for am__objects_1 = around line 500-550.

am__objects_1 = src/ar.$(OBJEXT) src/arscan.$(OBJEXT) src/commands.$(OBJEXT) ...
What to Modify: Append src/timetracker.o to the end of am__objects_1. Since $(OBJEXT) is defined as o in this Makefile, use src/timetracker.o.
Modified Line (partial excerpt):

am__objects_1 = src/ar.o src/arscan.o src/commands.o ... src/timetracker.o

Explanation:
Adding src/timetracker.o ensures it’s included in am_make_OBJECTS, which feeds into make_OBJECTS.
The $(OBJEXT) substitution is already handled by Automake, but since it’s o, you can write it directly as .o.
Step 4: Update the Linking Rule
Since timetracker.o is a C++ object file, the final linking step must use the C++ compiler (g++) instead of the C compiler (gcc) to correctly link C++ standard libraries and handle any C++-specific requirements. The linking command is defined by the LINK variable.

Where to Find: Search for LINK = around line 620-630, just after CCLD = $(CC).
Original Line:
makefile

Collapse

Wrap

Copy
LINK = $(CCLD) $(AM_CFLAGS) $(CFLAGS) $(AM_LDFLAGS) $(LDFLAGS) -o $@
What to Modify: Replace it to use $(CXX) and remove C-specific flags that aren’t needed for linking, relying on linker flags instead.
Modified Line:
makefile

Collapse

Wrap

Copy
LINK = $(CXX) $(AM_LDFLAGS) $(LDFLAGS) -o $@

- cd ./make_new
- make clean
- make
- cd ../libpng
- /home/ubuntu/efs/Xinrui/makefile_ninja_benchmarks/make_new/make clean
- sudo /home/ubuntu/efs/Xinrui/makefile_ninja_benchmarks/make_new/make -d > make_profile.txt
or
- cd ./make_new
- make clean
- make
- cd ..
- sh launch_make.sh /home/ubuntu/efs/Xinrui/makefile_ninja_benchmarks/libpng /home/ubuntu/efs/Xinrui/makefile_ninja_benchmarks/make_new/make

4. Compile the custom ninja
- python configure.py --bootstrap
- cd ..
- sh launch_ninja.sh /home/ubuntu/efs/Xinrui/makefile_ninja_benchmarks/libpng /home/ubuntu/efs/Xinrui/makefile_ninja_benchmarks/ninja_test/ninja

5. Alternative projects:
- OpenCV https://github.com/opencv/opencv
- Blender https://github.com/blender/blender
- LLVM https://github.com/llvm/llvm-project
- MySQL https://github.com/mysql/mysql-server