#pragma once
#include <cmath>
#include "jalansim/cuda_macros.hpp"

namespace jalansim::dynamics::models
{

    template <typename T>
    struct DiffDrive
    {
        static constexpr std::size_t STATE_DIM = 3;
        static constexpr std::size_t INPUT_DIM = 2;

        T wheel_r = T(0.098);
        T wheel_b = T(0.262);
        T vmin = T(-0.5);
        T vmax = T(2.0);
        T wmin = T(-2.0);
        T wmax = T(2.0);

        JALANSIM_HOST_DEVICE
        void rhs(const T *x, const T *u, T *dx, T dt = T(0.0)) const
        {
            const T v = u[0] < vmin ? vmin : (u[0] > vmax ? vmax : u[0]);
            const T w = u[1] < wmin ? wmin : (u[1] > wmax ? wmax : u[1]);

            dx[0] = v * std::cos(x[2]);
            dx[1] = v * std::sin(x[2]);
            dx[2] = w;
        }

        JALANSIM_HOST_DEVICE
        void reset() {}
    };

}
