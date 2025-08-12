cmake_minimum_required(VERSION 3.26 FATAL_ERROR)
project(b10-kernel LANGUAGES CXX CUDA)

# CMake
cmake_policy(SET CMP0169 OLD)
include(${CMAKE_CURRENT_LIST_DIR}/cmake/utils.cmake)
set(CMAKE_COLOR_DIAGNOSTICS ON)
set(CMAKE_VERBOSE_MAKEFILE ON CACHE BOOL "ON")
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_SHARED_LIBRARY_PREFIX "")

# Python
find_package(Python COMPONENTS Interpreter Development.Module ${SKBUILD_SABI_COMPONENT} REQUIRED)

# CXX
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")

# CUDA
enable_language(CUDA)
find_package(CUDAToolkit REQUIRED)
set_property(GLOBAL PROPERTY CUDA_SEPARABLE_COMPILATION ON)

message(STATUS "Detected CUDA_VERSION=${CUDA_VERSION}")
if ("${CUDA_VERSION}" VERSION_GREATER_EQUAL "13.0")
    message("CUDA_VERSION ${CUDA_VERSION} >= 13.0")
elseif ("${CUDA_VERSION}" VERSION_GREATER_EQUAL "12.8")
    message("CUDA_VERSION ${CUDA_VERSION} >= 12.8")
elseif ("${CUDA_VERSION}" VERSION_GREATER_EQUAL "12.4")
    message("CUDA_VERSION ${CUDA_VERSION} >= 12.4")
elseif ("${CUDA_VERSION}" VERSION_GREATER_EQUAL "12.1")
    message("CUDA_VERSION ${CUDA_VERSION} >= 12.1")
elseif ("${CUDA_VERSION}" VERSION_GREATER_EQUAL "11.8")
    message("CUDA_VERSION ${CUDA_VERSION} >= 11.8")
endif()

# Torch
find_package(Torch REQUIRED)
# clean Torch Flag
clear_cuda_arches(CMAKE_FLAG)

# ccache option
option(ENABLE_CCACHE "Whether to use ccache" ON)
find_program(CCACHE_FOUND ccache)
if(CCACHE_FOUND AND ENABLE_CCACHE AND DEFINED ENV{CCACHE_DIR})
    message(STATUS "Building with CCACHE enabled")
    set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE "ccache")
    set_property(GLOBAL PROPERTY RULE_LAUNCH_LINK "ccache")
endif()

include_directories(
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/csrc
)

set(B10_KERNEL_CUDA_FLAGS
    "-DNDEBUG"
    "-DOPERATOR_NAMESPACE=b10-kernel"
    "-O3"
    "-Xcompiler"
    "-fPIC"
    "-gencode=arch=compute_90,code=sm_90"
    "-std=c++17"
    "--expt-relaxed-constexpr"
    "--expt-extended-lambda"
    "--threads=32"

    # Suppress warnings
    "-Xcompiler=-Wconversion"
    "-Xcompiler=-fno-strict-aliasing"
)

option(B10_KERNEL_ENABLE_SM100A           "Enable SM100A"           ON)
option(B10_KERNEL_ENABLE_SM90A            "Enable SM90A"            ON)
option(B10_KERNEL_ENABLE_BF16             "Enable BF16"             ON)
option(B10_KERNEL_ENABLE_FP8              "Enable FP8"              ON)
option(B10_KERNEL_ENABLE_FP4              "Enable FP4"              ON)


if ("${CUDA_VERSION}" VERSION_GREATER_EQUAL "12.8" OR B10_KERNEL_ENABLE_SM100A)
    list(APPEND B10_KERNEL_CUDA_FLAGS
        "-gencode=arch=compute_100,code=sm_100"
        "-gencode=arch=compute_100a,code=sm_100a"
        "-gencode=arch=compute_101,code=sm_101"
        "-gencode=arch=compute_101a,code=sm_101a"
        "-gencode=arch=compute_120,code=sm_120"
        "-gencode=arch=compute_120a,code=sm_120a"
    )
else()
    list(APPEND B10_KERNEL_CUDA_FLAGS
        "-use_fast_math"
    )
endif()

if ("${CUDA_VERSION}" VERSION_GREATER_EQUAL "12.4" OR B10_KERNEL_ENABLE_SM90A)
    list(APPEND B10_KERNEL_CUDA_FLAGS
        "-gencode=arch=compute_90a,code=sm_90a"
    )
endif()

if (B10_KERNEL_ENABLE_BF16)
    list(APPEND B10_KERNEL_CUDA_FLAGS
        "-DFLASHINFER_ENABLE_BF16"
    )
endif()

if (B10_KERNEL_ENABLE_FP8)
    list(APPEND B10_KERNEL_CUDA_FLAGS
        "-DFLASHINFER_ENABLE_FP8"
        "-DFLASHINFER_ENABLE_FP8_E4M3"
        "-DFLASHINFER_ENABLE_FP8_E5M2"
    )
endif()

if ("${CUDA_VERSION}" VERSION_GREATER_EQUAL "12.8" OR B10_KERNEL_ENABLE_FP4)
    list(APPEND B10_KERNEL_CUDA_FLAGS
        "-DENABLE_NVFP4=1"
    )
endif()

string(REPLACE "-D__CUDA_NO_HALF_OPERATORS__"       "" CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS}")
string(REPLACE "-D__CUDA_NO_HALF_CONVERSIONS__"     "" CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS}")
string(REPLACE "-D__CUDA_NO_BFLOAT16_CONVERSIONS__" "" CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS}")
string(REPLACE "-D__CUDA_NO_HALF2_OPERATORS__"      "" CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS}")

# Add kernel files to the sources
set(SOURCES
    "csrc/norm.cu"
    "csrc/common_extensions.cc"
)

Python_add_library(common_ops MODULE USE_SABI ${SKBUILD_SABI_VERSION} WITH_SOABI ${SOURCES})

target_compile_options(common_ops PRIVATE $<$<COMPILE_LANGUAGE:CUDA>:${B10_KERNEL_CUDA_FLAGS}>)


find_package(Python3 COMPONENTS Interpreter REQUIRED)
execute_process(
    COMMAND ${Python3_EXECUTABLE} -c "import torch; print(int(torch._C._GLIBCXX_USE_CXX11_ABI))"
    OUTPUT_VARIABLE TORCH_CXX11_ABI
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
if(TORCH_CXX11_ABI STREQUAL "0")
    message(STATUS "Using old C++ ABI (-D_GLIBCXX_USE_CXX11_ABI=0)")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_GLIBCXX_USE_CXX11_ABI=0")
    set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -D_GLIBCXX_USE_CXX11_ABI=0")
else()
    message(STATUS "Using new C++11 ABI (-D_GLIBCXX_USE_CXX11_ABI=1)")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_GLIBCXX_USE_CXX11_ABI=1")
    set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -D_GLIBCXX_USE_CXX11_ABI=1")
endif()

target_link_libraries(common_ops PRIVATE ${TORCH_LIBRARIES} c10 cuda cublas cublasLt)

install(TARGETS common_ops LIBRARY DESTINATION b10_kernel)
