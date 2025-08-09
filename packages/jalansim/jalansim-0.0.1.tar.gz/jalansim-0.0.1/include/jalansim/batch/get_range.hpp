#pragma once
#include <cstddef>
#ifdef _OPENMP
#include <omp.h>
#endif

namespace jalansim::batch
{

#if JALANSIM_CUDA_ENABLED

    template <typename T, typename Sim>
    __global__ void range_kernel(
        Sim *sims,
        T *out,
        int num_beams,
        T fov,
        T max_range,
        std::size_t N)
    {
        std::size_t idx = blockIdx.x * blockDim.x + threadIdx.x;
        std::size_t total = N * std::size_t(num_beams);
        if (idx >= total)
            return;

        std::size_t sim_i = idx / num_beams;
        int beam_i = idx % num_beams;

        out[idx] = sims[sim_i]
                       .get_range_single(num_beams, fov, max_range, beam_i);
    }

    template <typename T, typename Sim>
    inline void get_range(
        Sim *sims,
        T *out,
        int num_beams,
        T fov,
        T max_range,
        std::size_t N)
    {
        std::size_t total = N * std::size_t(num_beams);
        std::size_t threads = JALANSIM_NUM_THREADS;
        std::size_t blocks = (total + threads - 1) / threads;
        range_kernel<T, Sim><<<blocks, threads>>>(sims, out, num_beams, fov, max_range, N);
    }

#else

    template <typename T, typename Sim>
    inline void get_range(
        Sim *sims,
        T *out,
        int num_beams,
        T fov,
        T max_range,
        std::size_t N)
    {
#pragma omp parallel for if (N > 1)
        for (std::size_t i = 0; i < N; ++i)
        {
            for (int b = 0; b < num_beams; ++b)
            {
                out[i * num_beams + b] =
                    sims[i].get_range_single(num_beams, fov, max_range, b);
            }
        }
    }

#endif

}