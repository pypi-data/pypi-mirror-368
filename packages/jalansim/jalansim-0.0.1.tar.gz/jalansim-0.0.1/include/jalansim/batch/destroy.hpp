#pragma once
#include <cstddef>
#include "jalansim/cuda_macros.hpp"

namespace jalansim::batch
{

#if JALANSIM_CUDA_ENABLED

    template <typename Sim>
    __global__ void destroy_kernel(Sim *sims, std::size_t N)
    {
        std::size_t i = blockIdx.x * blockDim.x + threadIdx.x;
        if (i < N)
        {
            sims[i].~Sim();
        }
    }
#endif

    template <typename Sim>
    inline void destroy(Sim *sims, std::size_t N)
    {
#if JALANSIM_CUDA_ENABLED
        std::size_t threads = JALANSIM_NUM_THREADS;
        std::size_t blocks = (N + threads - 1) / threads;
        destroy_kernel<<<blocks, threads>>>(sims, N);
#else
#pragma omp parallel for if (N > 1)
        for (std::size_t i = 0; i < N; ++i)
        {
            sims[i].~Sim();
        }
#endif
    }

}