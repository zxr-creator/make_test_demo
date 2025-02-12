cmake_minimum_required(VERSION 3.10)
project(DependencyGraph)

set(CMAKE_BUILD_TYPE Release)

# 指定 Ninja 作为构建工具
if(NOT CMAKE_GENERATOR STREQUAL "Ninja")
    message(WARNING "It's recommended to use Ninja: cmake -G Ninja .")
endif()

# 定义所有目标
foreach(node n1 n2 n3 n4 n5 n6 n7 n8 n9 n10 n11 n12 n13 n14 n15 n16 n17 n18)
    add_custom_command(OUTPUT ${node}
        COMMAND ${CMAKE_COMMAND} -E echo "Building ${node}"
        COMMAND ${CMAKE_COMMAND} -E touch ${node}
        COMMENT "Building ${node}"
    )
    add_custom_target(${node} DEPENDS ${node})
endforeach()

# 依赖关系
add_dependencies(n2 n1)
add_dependencies(n3 n1)
add_dependencies(n4 n3)
add_dependencies(n5 n3)
add_dependencies(n6 n5)
add_dependencies(n7 n5)
add_dependencies(n8 n6)
add_dependencies(n9 n6)
add_dependencies(n13 n3)
add_dependencies(n10 n7 n9 n13)
add_dependencies(n11 n10)
add_dependencies(n16 n14)
add_dependencies(n12 n11 n10 n16)
add_dependencies(n14 n13)
add_dependencies(n15 n13)
add_dependencies(n17 n15)
add_dependencies(n18 n12 n15)

# 定义 all 目标
add_custom_target(my_all DEPENDS n4 n2 n8 n9 n11 n12 n16 n17 n18)

# 清理目标
add_custom_target(my_clean
    COMMAND ${CMAKE_COMMAND} -E echo "Cleaning up..."
    COMMAND ${CMAKE_COMMAND} -E rm -f n1 n2 n3 n4 n5 n6 n7 n8 n9 n10 n11 n12 n13 n14 n15 n16 n17 n18
    COMMENT "Cleaning up..."
)
