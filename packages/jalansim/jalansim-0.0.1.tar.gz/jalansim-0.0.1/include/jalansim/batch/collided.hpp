#pragma once
#include <cstddef>
#include "jalansim/jalansim.hpp"
#include "jalansim/cuda_macros.hpp"

#ifdef _OPENMP
#include <omp.h>
#endif

namespace jalansim::batch
{

#if JALANSIM_CUDA_ENABLED
    template <typename Sim>
    __global__ void collided_kernel(const Sim *sims,
                                    bool *hits,
                                    std::size_t N)
    {
        std::size_t idx = blockIdx.x * blockDim.x + threadIdx.x;
        if (idx < N)
        {
            hits[idx] = sims[idx].collided();
        }
    }

    template <typename Sim>
    inline void collided(const Sim *sims,
                         bool *hits,
                         std::size_t N)
    {
        const int threadsPerBlock = JALANSIM_NUM_THREADS;
        const int blocks = static_cast<int>((N + threadsPerBlock - 1) / threadsPerBlock);
        collided_kernel<<<blocks, threadsPerBlock>>>(sims, hits, N);
    }

#else

    template <typename Sim>
    inline void collided(const Sim *sims,
                         bool *hits,
                         std::size_t N)
    {
#pragma omp parallel for if (N > 1)
        for (std::size_t i = 0; i < N; ++i)
        {
            hits[i] = sims[i].collided();
        }
    }

#endif

}
