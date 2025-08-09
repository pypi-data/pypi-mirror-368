#pragma once
#include <cmath>
#include "jalansim/cuda_macros.hpp"
#include "jalansim/controller/pid.hpp"

namespace jalansim::dynamics::models
{

    template <typename T>
    struct DiffDrivePID
    {
        static constexpr std::size_t STATE_DIM = 5;
        static constexpr std::size_t INPUT_DIM = 2;

        T wheel_r = 0.098;
        T wheel_b = 0.262;
        T wheel_J = 0.0024;

        T kp = 0.025, ki = 0.0, kd = 0.0;

        T torque_min = -50.0;
        T torque_max = 50.0;

        T w_min = -20.4082;
        T w_max = 20.4082;

        controller::PID<T> pid_r{kp, ki, kd, w_min, w_max, torque_min, torque_max};
        controller::PID<T> pid_l{kp, ki, kd, w_min, w_max, torque_min, torque_max};

        JALANSIM_HOST_DEVICE
        static T clamp(T v, T lo, T hi)
        {
            return v < lo ? lo : (v > hi ? hi : v);
        }

        JALANSIM_HOST_DEVICE
        void rhs(const T *x, const T *u, T *dx, T dt)
        {

            T v_sp = u[0], w_sp = u[1];
            T wr_sp = clamp((2 * v_sp + w_sp * wheel_b) / (2 * wheel_r), w_min, w_max);
            T wl_sp = clamp((2 * v_sp - w_sp * wheel_b) / (2 * wheel_r), w_min, w_max);

            T theta = x[2];
            T wr = x[3];
            T wl = x[4];

            T tau_r = pid_r.compute(wr_sp, wr, dt);
            T tau_l = pid_l.compute(wl_sp, wl, dt);

            T v_lin = (wr + wl) * wheel_r * 0.5;
            T theta_dot = (wr - wl) * wheel_r / wheel_b;

            dx[0] = v_lin * cos(theta);
            dx[1] = v_lin * sin(theta);
            dx[2] = theta_dot;

            T wr_dot_raw = tau_r / wheel_J;
            T wl_dot_raw = tau_l / wheel_J;

            dx[3] = clamp(wr_dot_raw, (w_min - wr) / dt, (w_max - wr) / dt);
            dx[4] = clamp(wl_dot_raw, (w_min - wl) / dt, (w_max - wl) / dt);
        }

        JALANSIM_HOST_DEVICE
        void reset()
        {
            pid_r.reset();
            pid_l.reset();
        }
    };

}
