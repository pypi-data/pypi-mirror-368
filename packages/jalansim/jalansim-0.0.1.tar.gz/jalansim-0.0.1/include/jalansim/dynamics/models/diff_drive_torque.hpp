#pragma once
#include <cmath>
#include "jalansim/cuda_macros.hpp"

namespace jalansim::dynamics::models
{

    template <typename T = double>
    struct DiffDriveTorque
    {

        static constexpr std::size_t STATE_DIM = 5;
        static constexpr std::size_t INPUT_DIM = 2;

        T wheel_r = T(0.098);
        T wheel_b = T(0.262);
        T wheel_J = T(0.0024);

        T torque_min = T(-50.0);
        T torque_max = T(50.0);

        T w_min = T(-20.4082);
        T w_max = T(20.4082);

        JALANSIM_HOST_DEVICE
        static T clamp(T v, T lo, T hi)
        {
            return v < lo ? lo : (v > hi ? hi : v);
        }

        JALANSIM_HOST_DEVICE
        void rhs(const T *x,
                 const T *u,
                 T *dx,
                 T dt = T(0)) const
        {

            const T theta = x[2];
            const T wr = x[3];
            const T wl = x[4];

            const T torque_r = clamp(u[0], torque_min, torque_max);
            const T torque_l = clamp(u[1], torque_min, torque_max);

            const T v_linear = (wr + wl) * wheel_r * T(0.5);
            const T theta_dot = (wr - wl) * wheel_r / wheel_b;

            dx[0] = v_linear * std::cos(theta);
            dx[1] = v_linear * std::sin(theta);
            dx[2] = theta_dot;

            const T wr_dot_raw = torque_r / wheel_J;
            const T wl_dot_raw = torque_l / wheel_J;

            const T dt_safe = dt > T(0) ? dt : T(1);
            dx[3] = clamp(wr_dot_raw,
                          (w_min - wr) / dt_safe,
                          (w_max - wr) / dt_safe);
            dx[4] = clamp(wl_dot_raw,
                          (w_min - wl) / dt_safe,
                          (w_max - wl) / dt_safe);
        }

        JALANSIM_HOST_DEVICE
        void reset() {}
    };

}
