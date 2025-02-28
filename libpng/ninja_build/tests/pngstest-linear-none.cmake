# test.cmake.in

# Copyright (c) 2024 Cosmin Truta
# Copyright (c) 2016 Glenn Randers-Pehrson
# Written by Roger Leigh, 2016
#
# Use, modification and distribution are subject to
# the same licensing terms and conditions as libpng.
# Please see the copyright notice in png.h or visit
# http://libpng.org/pub/png/src/libpng-LICENSE.txt
#
# SPDX-License-Identifier: libpng-2.0

set(TEST_OPTIONS "--tmpfile;linear-none-;--log")
set(TEST_FILES "/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/gray-1-linear-tRNS.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/gray-1-linear.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/gray-16-linear-tRNS.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/gray-16-linear.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/gray-2-linear-tRNS.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/gray-2-linear.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/gray-4-linear-tRNS.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/gray-4-linear.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/gray-8-linear-tRNS.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/gray-8-linear.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/palette-1-linear-tRNS.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/palette-1-linear.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/palette-2-linear-tRNS.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/palette-2-linear.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/palette-4-linear-tRNS.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/palette-4-linear.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/palette-8-linear-tRNS.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/palette-8-linear.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/rgb-16-linear-tRNS.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/rgb-16-linear.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/rgb-8-linear-tRNS.png;/home/ued520/makefile_ninja_benchmarks/libpng/contrib/testpngs/rgb-8-linear.png")

foreach(file ${TEST_FILES})
  file(TO_NATIVE_PATH "${file}" native_file)
  list(APPEND NATIVE_TEST_FILES "${native_file}")
endforeach()

# Add the directory containing libpng to the PATH (Windows only)
if(WIN32)
  get_filename_component(LIBPNG_DIR "${LIBPNG}" PATH)
  file(TO_NATIVE_PATH "${LIBPNG_DIR}" LIBPNG_DIR)
  set(ENV{PATH} "${LIBPNG_DIR};$ENV{PATH}")
endif()

string(JOIN " " TEST_COMMAND_STRING "${TEST_COMMAND}" ${TEST_OPTIONS} ${NATIVE_TEST_FILES})
message(STATUS "Running ${TEST_COMMAND_STRING}")
execute_process(COMMAND "${TEST_COMMAND}" ${TEST_OPTIONS} ${NATIVE_TEST_FILES}
                RESULT_VARIABLE TEST_STATUS)
if(TEST_STATUS)
  message(FATAL_ERROR "Returned failed status ${TEST_STATUS}!")
endif()
