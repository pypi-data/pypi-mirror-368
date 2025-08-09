#pragma once
#include <cstddef>
#include "jalansim/cuda_macros.hpp"

namespace jalansim::batch
{

#if JALANSIM_CUDA_ENABLED

    template <typename Sim>
    __global__ void init_kernel(Sim *sims, typename Sim::DynamicsModel dyn, typename Sim::Collision col, std::size_t N)
    {
        std::size_t i = blockIdx.x * blockDim.x + threadIdx.x;
        if (i < N)
        {
            new (&sims[i]) Sim(dyn, col);
        }
    }

#endif

    template <typename Sim>
    inline void init(Sim *sims, typename Sim::DynamicsModel dyn, typename Sim::Collision col, std::size_t N)
    {
#if JALANSIM_CUDA_ENABLED
        std::size_t threads = JALANSIM_NUM_THREADS;
        std::size_t blocks = (N + threads - 1) / threads;
        init_kernel<<<blocks, threads>>>(sims, dyn, col, N);
#else
#pragma omp parallel for if (N > 1)
        for (std::size_t i = 0; i < N; ++i)
        {
            new (&sims[i]) Sim(dyn, col);
        }
#endif
    }

}