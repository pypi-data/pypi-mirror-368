#pragma once
#include <string>
#include <stdexcept>

#if defined(__CUDACC__) || defined(JALANSIM_USE_CUDA)
    #define JALANSIM_CUDA_ENABLED 1
    
    #ifndef JALANSIM_NUM_THREADS
    #define JALANSIM_NUM_THREADS 256
    #endif

    #include <cuda_runtime.h>
    #define JALANSIM_HOST_DEVICE __host__ __device__

    inline void check_cuda(const char *where = "") {
        cudaError_t err = cudaDeviceSynchronize();
        if (err != cudaSuccess) {
            std::string msg = std::string(where) + ": " + cudaGetErrorString(err);
            throw std::runtime_error(msg);
        }
    }

#else
    #define JALANSIM_CUDA_ENABLED 0

    #define JALANSIM_HOST_DEVICE
#endif