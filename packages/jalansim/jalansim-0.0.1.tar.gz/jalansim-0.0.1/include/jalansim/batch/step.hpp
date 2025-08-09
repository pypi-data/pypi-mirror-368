#pragma once
#include <cstddef>
#include "jalansim/cuda_macros.hpp"

namespace jalansim::batch
{

#if JALANSIM_CUDA_ENABLED

    template <typename T, typename Sim>
    __global__ void step_kernel(Sim *sims,
                                const T *u,
                                T dt,
                                std::size_t N)
    {
        std::size_t i = blockIdx.x * blockDim.x + threadIdx.x;
        if (i < N)
        {

            const T *inputs = &u[i * Sim::INPUT_DIM];
            sims[i].step(inputs, dt);
        }
    }
#endif

    template <typename T, typename Sim>
    inline void step(Sim *sims,
                     const T *u,
                     T dt,
                     std::size_t N)
    {
#if JALANSIM_CUDA_ENABLED
        std::size_t threads = JALANSIM_NUM_THREADS;
        std::size_t blocks = (N + threads - 1) / threads;
        step_kernel<T, Sim><<<blocks, threads>>>(sims, u, dt, N);
#else
#pragma omp parallel for if (N > 1)
        for (std::size_t i = 0; i < N; ++i)
        {
            const T *inputs = &u[i * Sim::INPUT_DIM];
            sims[i].step(inputs, dt);
        }
#endif
    }

}