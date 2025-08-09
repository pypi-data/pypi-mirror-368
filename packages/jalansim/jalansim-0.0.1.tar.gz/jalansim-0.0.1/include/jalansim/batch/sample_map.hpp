#pragma once

#include <cstddef>
#include <vector>
#include <ctime>
#include <numeric>

#include "jalansim/map/map.hpp"
#include "jalansim/cuda_macros.hpp"
#include "jalansim/map/map_collection.hpp"

#ifdef _OPENMP
#include <omp.h>
#endif

namespace jalansim::batch
{

#if JALANSIM_CUDA_ENABLED
    template <typename T, class Sim>
    __global__ void sample_map_kernel(Sim *sims,
                                      jalansim::map::MapCollection<T> *map_collection,
                                      unsigned int base_rng_seed,
                                      std::size_t N,
                                      const bool *mask)
    {
        std::size_t i = blockIdx.x * blockDim.x + threadIdx.x;
        if (i < N)
        {
            if (mask && !mask[i])
            {
                return;
            }
            if (!map_collection || !sims)
                return;

            unsigned int thread_local_seed = base_rng_seed + static_cast<unsigned int>(i);
            jalansim::map::Map<T> *sampled_map = map_collection->sample(thread_local_seed);

            sims[i].set_map(sampled_map);
        }
    }
#endif

    template <typename T, class Sim>
    inline void sample_map(Sim *sims,
                           jalansim::map::MapCollection<T> *map_collection,
                           std::size_t N,
                           unsigned int base_rng_seed = 0,
                           const bool *mask = nullptr)
    {
        if (N == 0 || !sims || !map_collection)
        {
            return;
        }

        if (base_rng_seed == 0)
        {
            base_rng_seed = static_cast<unsigned int>(std::time(nullptr));
        }

#if JALANSIM_CUDA_ENABLED
        const std::size_t threads_per_block = JALANSIM_NUM_THREADS;
        const std::size_t num_blocks = (N + threads_per_block - 1) / threads_per_block;

        sample_map_kernel<T, Sim><<<num_blocks, threads_per_block>>>(sims, map_collection, base_rng_seed, N, mask);

#else
#pragma omp parallel if (N > 1)
        {
            unsigned int thread_local_rng_seed = base_rng_seed + static_cast<unsigned int>(omp_get_thread_num());

#pragma omp for schedule(static)
            for (std::size_t i = 0; i < N; ++i)
            {
                if (!mask || mask[i])
                {
                    jalansim::map::Map<T> *sampled_map = map_collection->sample(thread_local_rng_seed);
                    sims[i].set_map(sampled_map);
                }
            }
        }
#endif
    }

}
