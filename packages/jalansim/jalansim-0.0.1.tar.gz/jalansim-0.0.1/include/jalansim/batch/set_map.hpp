#pragma once
#include <cstddef>
#include "jalansim/map/map.hpp"
#include "jalansim/cuda_macros.hpp"

#ifdef _OPENMP
#include <omp.h>
#endif

namespace jalansim::batch
{

#if JALANSIM_CUDA_ENABLED

    template <typename T, class Sim>
    __global__ void set_map_kernel(Sim *sims, jalansim::map::Map<T> *map, std::size_t N)
    {
        std::size_t i = blockIdx.x * blockDim.x + threadIdx.x;
        if (i < N)
            sims[i].set_map(map);
    }
#endif

    template <typename T, class Sim>
    inline void set_map(Sim *sims,
                        jalansim::map::Map<T> *map,
                        std::size_t N)
    {
#if JALANSIM_CUDA_ENABLED
        const std::size_t threads = JALANSIM_NUM_THREADS;
        const std::size_t blocks = (N + threads - 1) / threads;
        set_map_kernel<T, Sim><<<blocks, threads>>>(sims, map, N);
#else

#pragma omp parallel for if (N > 1)
        for (std::size_t i = 0; i < N; ++i)
        {
            sims[i].set_map(map);
        }
#endif
    }

}
