#pragma once

#include <cstddef>
#ifdef _OPENMP
#include <omp.h>
#endif

namespace jalansim::batch
{

#if JALANSIM_CUDA_ENABLED

    template <typename T, typename Sim>
    __global__ void state_kernel(const Sim *sims,
                                 T *out,
                                 std::size_t N)
    {
        constexpr std::size_t D = Sim::STATE_DIM;

        std::size_t i = blockIdx.x * blockDim.x + threadIdx.x;
        if (i >= N)
            return;

        const T *s = sims[i].get_state();
        T *dst = out + i * D;

#pragma unroll
        for (std::size_t d = 0; d < D; ++d)
            dst[d] = s[d];
    }

    template <typename T, typename Sim>
    inline void get_state(const Sim *sims,
                          T *out,
                          std::size_t N)
    {
        constexpr std::size_t threads = JALANSIM_NUM_THREADS;
        std::size_t blocks = (N + threads - 1) / threads;

        state_kernel<T, Sim><<<blocks, threads>>>(sims, out, N);
    }

#else

    template <typename T, typename Sim>
    inline void get_state(const Sim *sims,
                          T *out,
                          std::size_t N)
    {
        constexpr std::size_t D = Sim::STATE_DIM;

#pragma omp parallel for if (N > 1)
        for (std::size_t i = 0; i < N; ++i)
        {
            const T *src = sims[i].get_state();
            T *dst = out + i * D;
            for (std::size_t d = 0; d < D; ++d)
                dst[d] = src[d];
        }
    }

#endif

}
