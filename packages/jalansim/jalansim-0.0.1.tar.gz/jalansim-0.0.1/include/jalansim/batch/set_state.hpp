#pragma once
#include <cstddef>
#include "jalansim/cuda_macros.hpp"
#ifdef _OPENMP
#include <omp.h>
#endif

namespace jalansim::batch
{

#if JALANSIM_CUDA_ENABLED
    template <typename T, typename Sim>
    __global__ void set_state_kernel(
        Sim *sims,
        const T *states,
        const bool *mask,
        std::size_t N)
    {
        std::size_t i = blockIdx.x * blockDim.x + threadIdx.x;
        if (i >= N)
            return;
        if (mask && !mask[i])
            return;
        sims[i].set_state(states + i * Sim::STATE_DIM);
    }
#endif

    template <typename T, typename Sim>
    inline void set_state(
        Sim *sims,
        const T *states,
        std::size_t N,
        const bool *mask = nullptr)
    {
#if JALANSIM_CUDA_ENABLED
        std::size_t threads = JALANSIM_NUM_THREADS;
        std::size_t blocks = (N + threads - 1) / threads;
        set_state_kernel<T, Sim><<<blocks, threads>>>(sims, states, mask, N);
#else
#pragma omp parallel for if (N > 1)
        for (std::size_t i = 0; i < N; ++i)
        {
            if (mask && !mask[i])
                continue;
            sims[i].set_state(states + i * Sim::STATE_DIM);
        }
#endif
    }

}