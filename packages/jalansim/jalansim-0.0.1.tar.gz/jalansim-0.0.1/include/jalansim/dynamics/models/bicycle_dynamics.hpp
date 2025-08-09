#pragma once
#include <jalansim/cuda_macros.hpp>
#include <cmath>
#include "bicycle.hpp"

namespace jalansim::dynamics::models
{

    template <typename T>
    struct BicycleDynamics
    {

        static constexpr std::size_t STATE_DIM = 7;
        static constexpr std::size_t INPUT_DIM = 2;

        T a = 0.15875;
        T b = 0.17145;
        T h = 0.074;

        T m = 3.74;
        T I_z = 0.04712;

        T mu = 1.0489;
        T C_Sf = 4.718;
        T C_Sr = 5.4562;

        T delta_min = -0.4189;
        T delta_max = 0.4189;
        T delta_dot_min = -3.2;
        T delta_dot_max = 3.2;

        T acc_min = -5.0;
        T acc_max = 3.0;

        T v_min = 0.0;
        T v_max = 3.0;

        static constexpr T g = 9.81;

        JALANSIM_HOST_DEVICE
        static T clamp(T v, T lo, T hi)
        {
            return v < lo ? lo : (v > hi ? hi : v);
        }

        JALANSIM_HOST_DEVICE
        T steering_constraints(T delta, T delta_dot_cmd) const
        {

            T d_dot = clamp(delta_dot_cmd, delta_dot_min, delta_dot_max);

            return d_dot;
        }

        JALANSIM_HOST_DEVICE
        T accel_constraints(T v, T a_cmd) const
        {
            return clamp(a_cmd, acc_min, acc_max);
        }

        JALANSIM_HOST_DEVICE
        void rhs(const T *x, const T *u_cmd,
                 T *dx, T dt) const
        {

            const T X = x[0];
            const T Y = x[1];
            const T psi = x[2];
            const T v = x[3];
            const T delta = x[4];
            const T psi_dot = x[5];
            const T beta = x[6];

            T delta_dot = steering_constraints(delta, u_cmd[0]);
            if (dt > 0.0)
            {
                T next = delta + delta_dot * dt;
                if (next > delta_max)
                    delta_dot = (delta_max - delta) / dt;
                if (next < delta_min)
                    delta_dot = (delta_min - delta) / dt;
            }
            T a_long = accel_constraints(v, u_cmd[1]);
            if (dt > 0.0)
            {
                T next = v + a_long * dt;
                if (next < v_min)
                    a_long = (v_min - v) / dt;
                if (next > v_max)
                    a_long = (v_max - v) / dt;
            }

            if (v < 1.0)
            {
                const T lwb = a + b;
                const T beta = std::atan2(b * std::tan(delta), lwb);

                dx[0] = v * std::cos(psi + beta);
                dx[1] = v * std::sin(psi + beta);
                dx[2] = v / lwb * std::tan(delta);
                dx[3] = a_long;
                dx[4] = delta_dot;

                T psi_dd = a_long / lwb * std::tan(delta) +
                           v / (lwb * std::cos(delta) * std::cos(delta)) * delta_dot;
                T d_beta = 0.0;

                dx[5] = psi_dd;
                dx[6] = d_beta;
                return;
            }

            const T lf = a;
            const T lr = b;

            dx[0] = v * std::cos(beta + psi);
            dx[1] = v * std::sin(beta + psi);
            dx[2] = psi_dot;
            dx[3] = a_long;
            dx[4] = delta_dot;

            dx[5] =
                -mu * m / (v * I_z * (lr + lf)) *
                    (lf * lf * C_Sf * (g * lr - a_long * h) +
                     lr * lr * C_Sr * (g * lf + a_long * h)) *
                    psi_dot +
                mu * m / (I_z * (lr + lf)) *
                    (lr * C_Sr * (g * lf + a_long * h) -
                     lf * C_Sf * (g * lr - a_long * h)) *
                    beta +
                mu * m / (I_z * (lr + lf)) *
                    lf * C_Sf * (g * lr - a_long * h) * delta;

            dx[6] =
                (mu / (v * v * (lr + lf)) *
                     (C_Sr * (g * lf + a_long * h) * lr -
                      C_Sf * (g * lr - a_long * h) * lf) -
                 1.0) *
                    psi_dot -
                mu / (v * (lr + lf)) *
                    (C_Sr * (g * lf + a_long * h) +
                     C_Sf * (g * lr - a_long * h)) *
                    beta +
                mu / (v * (lr + lf)) *
                    (C_Sf * (g * lr - a_long * h)) * delta;
        }

        JALANSIM_HOST_DEVICE
        void reset() {}
    };

}
