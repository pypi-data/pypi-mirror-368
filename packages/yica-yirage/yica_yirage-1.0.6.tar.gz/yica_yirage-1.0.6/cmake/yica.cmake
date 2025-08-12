# YICA 后端 CMake 配置
# 用于集成 YICA 硬件支持到 Mirage 构建系统

include_guard()

# YICA 相关选项
option(BUILD_YICA_BACKEND "Build YICA backend support" OFF)
option(ENABLE_YICA_OPTIMIZATION "Enable YICA-specific optimizations" OFF)
option(ENABLE_YICA_SIMULATION "Enable YICA simulation mode for testing" ON)
option(ENABLE_YCCL_DISTRIBUTED "Enable YCCL distributed communication" OFF)
option(ENABLE_YIS_TRANSPILER "Enable YIS instruction transpiler" OFF)

# YICA 路径配置
set(YICA_ROOT_PATH "${CMAKE_CURRENT_SOURCE_DIR}/yica" CACHE PATH "YICA root directory")
set(YICA_INCLUDE_DIR "${YICA_ROOT_PATH}/include" CACHE PATH "YICA include directory")
set(YICA_LIBRARY_DIR "${YICA_ROOT_PATH}/lib" CACHE PATH "YICA library directory")

# YICA 版本信息
set(YICA_VERSION_MAJOR 1)
set(YICA_VERSION_MINOR 0)
set(YICA_VERSION_PATCH 0)
set(YICA_VERSION "${YICA_VERSION_MAJOR}.${YICA_VERSION_MINOR}.${YICA_VERSION_PATCH}")

message(STATUS "YICA Backend Configuration:")
message(STATUS "  Build YICA Backend: ${BUILD_YICA_BACKEND}")
message(STATUS "  YICA Optimization: ${ENABLE_YICA_OPTIMIZATION}")
message(STATUS "  YICA Simulation: ${ENABLE_YICA_SIMULATION}")
message(STATUS "  YICA Version: ${YICA_VERSION}")

# 查找 YICA 库
function(find_yica_libraries)
    if(BUILD_YICA_BACKEND)
        # 查找 YICA 核心库
        find_library(YICA_CORE_LIBRARY
            NAMES yica_core libyica_core
            PATHS ${YICA_LIBRARY_DIR}
            NO_DEFAULT_PATH
        )
        
        # 查找头文件
        find_path(YICA_INCLUDE_PATH
            NAMES yica/yica.h
            PATHS ${YICA_INCLUDE_DIR}
            NO_DEFAULT_PATH
        )
        
        # 设置全局变量
        set(YICA_LIBRARIES ${YICA_CORE_LIBRARY} PARENT_SCOPE)
        set(YICA_INCLUDE_PATH ${YICA_INCLUDE_PATH} PARENT_SCOPE)
        set(YICA_FOUND TRUE PARENT_SCOPE)
    endif()
endfunction()

# 配置 YICA 编译器标志
function(configure_yica_compile_flags)
    if(BUILD_YICA_BACKEND)
        set(YICA_COMPILE_FLAGS
            -DYICA_BACKEND_ENABLED=1
            -DYICA_VERSION_MAJOR=${YICA_VERSION_MAJOR}
        )
        
        if(ENABLE_YICA_OPTIMIZATION)
            list(APPEND YICA_COMPILE_FLAGS -DYICA_OPTIMIZATION_ENABLED=1)
        endif()
        
        if(ENABLE_YICA_SIMULATION)
            list(APPEND YICA_COMPILE_FLAGS -DYICA_SIMULATION_MODE=1)
        endif()
        
        set(YICA_COMPILE_FLAGS ${YICA_COMPILE_FLAGS} PARENT_SCOPE)
    endif()
endfunction()

# 主要配置函数
function(configure_yica)
    if(BUILD_YICA_BACKEND)
        message(STATUS "Configuring YICA backend support...")
        find_yica_libraries()
        configure_yica_compile_flags()
        message(STATUS "YICA backend configuration completed")
    endif()
endfunction() 