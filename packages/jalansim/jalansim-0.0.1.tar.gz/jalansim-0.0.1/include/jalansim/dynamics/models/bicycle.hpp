#pragma once
#include <jalansim/cuda_macros.hpp>
#include <cmath>

namespace jalansim::dynamics::models
{

    template <typename T>
    struct Bicycle
    {

        static constexpr std::size_t STATE_DIM = 5;
        static constexpr std::size_t INPUT_DIM = 2;

        T a;
        T b;

        T delta_min;
        T delta_max;
        T delta_dot_min;
        T delta_dot_max;

        T v_min;
        T v_max;

        T acc_min;
        T acc_max;

        JALANSIM_HOST_DEVICE
        Bicycle() : a(0.15875), b(0.17145),
                    delta_min(-0.4189), delta_max(0.4189),
                    delta_dot_min(-3.2), delta_dot_max(3.2),
                    v_min(-1.0), v_max(10.0),
                    acc_min(-9.51), acc_max(9.51)
        {
        }

        JALANSIM_HOST_DEVICE
        Bicycle(T a_, T b_, T delta_min_, T delta_max_,
                T delta_dot_min_, T delta_dot_max_,
                T v_min_, T v_max_, T acc_min_, T acc_max_) : a(a_), b(b_),
                                                              delta_min(delta_min_), delta_max(delta_max_),
                                                              delta_dot_min(delta_dot_min_), delta_dot_max(delta_dot_max_),
                                                              v_min(v_min_), v_max(v_max_),
                                                              acc_min(acc_min_), acc_max(acc_max_)
        {
        }

        JALANSIM_HOST_DEVICE
        static T clamp(T v, T lo, T hi)
        {
            return v < lo ? lo : (v > hi ? hi : v);
        }

        JALANSIM_HOST_DEVICE
        void rhs(const T *x,
                 const T *u_cmd,
                 T *dx,
                 T dt) const
        {

            const T pos_x = x[0];
            const T pos_y = x[1];
            const T psi = x[2];
            const T v = x[3];
            const T delta = x[4];

            T delta_dot = clamp(u_cmd[0], delta_dot_min, delta_dot_max);

            if (dt > 0.0)
            {
                T delta_next = delta + delta_dot * dt;
                if (delta_next > delta_max)
                    delta_dot = (delta_max - delta) / dt;
                if (delta_next < delta_min)
                    delta_dot = (delta_min - delta) / dt;
            }

            T a_long = clamp(u_cmd[1], acc_min, acc_max);

            if (dt > 0.0)
            {
                T v_next = v + a_long * dt;
                if (v_next < v_min)
                    a_long = (v_min - v) / dt;
                if (v_next > v_max)
                    a_long = (v_max - v) / dt;
            }

            const T l = a + b;
            const T beta = std::atan2(b * std::tan(delta), l);

            dx[0] = v * std::cos(psi + beta);
            dx[1] = v * std::sin(psi + beta);
            dx[2] = v / l * std::tan(delta);
            dx[3] = a_long;
            dx[4] = delta_dot;
        }

        JALANSIM_HOST_DEVICE
        void reset() {}
    };

}
