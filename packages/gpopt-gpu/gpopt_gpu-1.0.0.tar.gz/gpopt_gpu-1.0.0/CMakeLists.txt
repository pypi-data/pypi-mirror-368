cmake_minimum_required(VERSION 3.18)
project(gpopt LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_STANDARD 17)
set(CMAKE_CUDA_STANDARD_REQUIRED ON)

find_package(CUDAToolkit REQUIRED)
find_package(pybind11 REQUIRED)

pybind11_add_module(gpopt_gpu
    bindings.cpp
    src/core/Evolution.cu
    src/cuda/kernels.cu
)

target_include_directories(gpopt_gpu PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(gpopt_gpu PRIVATE CUDA::cudart)

set_target_properties(gpopt_gpu PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/gpopt"
)