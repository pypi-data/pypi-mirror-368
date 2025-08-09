cmake_minimum_required(VERSION 3.20)

option(WITH_CUDA "Build CUDA demo target" OFF)
option(WITH_OPENMP "Build with OpenMP support" ON)
option(WITH_PYTHON "Build Python bindings" ON)
option(WITH_DEMOS "Build demo executables" OFF)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Release" CACHE STRING 
      "Choose the type of build (Debug, Release, RelWithDebInfo, MinSizeRel)" FORCE)
endif()

if(EXISTS "/opt/homebrew/opt/llvm")
    set(BREW_LLVM_PREFIX "/opt/homebrew/opt/llvm")
    if(EXISTS "${BREW_LLVM_PREFIX}/bin/clang")
        message(STATUS "Detected /opt/homebrew → using Homebrew LLVM‐clang")
        set(CMAKE_C_COMPILER   "${BREW_LLVM_PREFIX}/bin/clang"   CACHE FILEPATH "" FORCE)
        set(CMAKE_CXX_COMPILER "${BREW_LLVM_PREFIX}/bin/clang++" CACHE FILEPATH "" FORCE)
        set(ENV{PATH} "${BREW_LLVM_PREFIX}/bin:$ENV{PATH}")
    endif()
endif()

if (WITH_CUDA)
    set(CMAKE_CUDA_SEPARABLE_COMPILATION ON)
    set(CMAKE_CUDA_ARCHITECTURES 52 60 70 75 86)
    set(CMAKE_CUDA_FLAGS_RELEASE
        "${CMAKE_CUDA_FLAGS_RELEASE} -O3 --use_fast_math")
endif()

# — Project definition (switch in/out CUDA language) —
if (WITH_CUDA)
    project(jalansim LANGUAGES CXX CUDA)
    enable_language(CUDA)
else()
    project(jalansim LANGUAGES CXX)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POLICY_VERSION_MINIMUM 3.5)

if (WITH_OPENMP)

    find_package(OpenMP QUIET)
    if(OpenMP_CXX_FOUND)
        message(STATUS "OpenMP found, enabling OpenMP support")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
    else()
        message(WARNING "OpenMP not found, disabling OpenMP support")
    endif()
endif()


if (WITH_PYTHON)
    # Set C++ standard for nanobind compatibility
    set(CMAKE_CXX_STANDARD 17)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)
    set(CMAKE_CXX_EXTENSIONS OFF)

    if (CMAKE_VERSION VERSION_LESS 3.18)
        set(PYTHON_DEV_MODULE Development)
    else()
        set(PYTHON_DEV_MODULE Development.Module)
    endif()

    set(Python3_FIND_VIRTUALENV "STANDARD")

    find_package(Python 3.8 COMPONENTS Interpreter ${PYTHON_DEV_MODULE} REQUIRED)

    include(FetchContent)

    FetchContent_Declare(
        nanobind
        GIT_REPOSITORY https://github.com/wjakob/nanobind.git
        GIT_TAG        v2.7.0
    )

    FetchContent_MakeAvailable(nanobind)

endif()

# — Optimization flags for C++ —
# Only applied in Release
set(CMAKE_CXX_FLAGS_RELEASE
    "${CMAKE_CXX_FLAGS_RELEASE} -O3 -march=native -ffast-math")

# (Optional) Tweak RelWithDebInfo, MinSizeRel too:
set(CMAKE_CXX_FLAGS_RELWITHDEBINFO
    "${CMAKE_CXX_FLAGS_RELWITHDEBINFO} -O2 -g")
set(CMAKE_CXX_FLAGS_MINSIZEREL
    "${CMAKE_CXX_FLAGS_MINSIZEREL} -Os")

set(JALANSIM_SOURCES
    src/stb_image_impl.cpp
)

# — Optimization flags for CUDA (if enabled) —

# ----- header paths -----------------------------------------------------
set(EXTERNAL_DIR ${CMAKE_CURRENT_SOURCE_DIR}/external)

add_library(jalansim INTERFACE)
target_include_directories(jalansim INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<BUILD_INTERFACE:${EXTERNAL_DIR}>)

if (WITH_DEMOS)
    # ----- CPU demo ---------------------------------------------------------
    add_executable(jalansim_cpu
        src/demos/jalansim_cpu.cpp
        ${JALANSIM_SOURCES})
    target_link_libraries(jalansim_cpu PRIVATE jalansim)

    add_executable(jalansim_batch_cpu
        src/demos/jalansim_batch_cpu.cpp
        ${JALANSIM_SOURCES})
    target_link_libraries(jalansim_batch_cpu PRIVATE jalansim)

    if(OpenMP_CXX_FOUND)
        target_link_libraries(jalansim_batch_cpu PRIVATE OpenMP::OpenMP_CXX)
    endif()

    # ----- CUDA demo --------------------------------------------------------
    if (WITH_CUDA)
        add_executable(jalansim_batch_cuda
            src/demos/jalansim_batch_cuda.cu
            ${JALANSIM_SOURCES})
        target_link_libraries(jalansim_batch_cuda PRIVATE jalansim)
        target_compile_definitions(jalansim_batch_cuda PRIVATE JALANSIM_USE_CUDA)
    endif()

    # ----- Map loader demo ----------------------------------------------------
    add_executable(map_loader_cpu
        src/demos/map_loader_cpu.cpp
        ${JALANSIM_SOURCES})
    target_link_libraries(map_loader_cpu PRIVATE jalansim)

    if(OpenMP_CXX_FOUND)
        target_link_libraries(map_loader_cpu PRIVATE OpenMP::OpenMP_CXX)
    endif()


    # ----- Map loader demo with CUDA ----------------------------------------
    if (WITH_CUDA)
        add_executable(map_loader_cuda
            src/demos/map_loader_cuda.cu
            ${JALANSIM_SOURCES})
        target_link_libraries(map_loader_cuda PRIVATE jalansim)
        target_compile_definitions(map_loader_cuda PRIVATE JALANSIM_USE_CUDA)
    endif()
endif()

# ----- Python bindings ---------------------------------------------------
if (WITH_PYTHON)
    if (WITH_CUDA)
        nanobind_add_module(_core_cuda  # Rename target to jalansim
            src/bindings/bindings_cuda.cu
            ${JALANSIM_SOURCES}
        )
        target_link_libraries(_core_cuda PRIVATE jalansim)
        install(TARGETS _core_cuda
                LIBRARY DESTINATION jalansim     # Unix (.so)
                RUNTIME DESTINATION jalansim)    # Windows (.pyd)
    endif()

    nanobind_add_module(_core_cpu
        src/bindings/bindings_cpu.cpp
        ${JALANSIM_SOURCES}
    )
    target_link_libraries(_core_cpu PRIVATE jalansim)
    if(OpenMP_CXX_FOUND)
        target_link_libraries(_core_cpu PRIVATE OpenMP::OpenMP_CXX)
    endif()
    install(TARGETS _core_cpu
            LIBRARY DESTINATION jalansim     # Unix (.so)
            RUNTIME DESTINATION jalansim)    # Windows (.pyd)

endif()
