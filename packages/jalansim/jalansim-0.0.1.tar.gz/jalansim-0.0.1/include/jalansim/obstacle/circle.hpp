#pragma once
#include "jalansim/cuda_macros.hpp"

namespace jalansim::obstacle
{

    template <typename T, std::size_t N_TRAJ>
    struct CircleObstacle
    {
        T radius = T(0.1);
        T traj_x[N_TRAJ] = {T(0.0)};
        T traj_y[N_TRAJ] = {T(0.0)};
        T traj_time[N_TRAJ] = {T(0.0)};

        JALANSIM_HOST_DEVICE
        bool collided(T x, T y) const
        {

            T dx = x - traj_x[0];
            T dy = y - traj_y[0];
            return (dx * dx + dy * dy <= radius * radius);
        }

        JALANSIM_HOST_DEVICE
        T distance(T x, T y) const
        {

            T dx = x - traj_x[0];
            T dy = y - traj_y[0];
            return std::sqrt(dx * dx + dy * dy);
        }

        JALANSIM_HOST_DEVICE
        void set_radius(T r)
        {
            radius = r;
        }

        JALANSIM_HOST_DEVICE
        T get_radius() const
        {
            return radius;
        }

        JALANSIM_HOST_DEVICE
        void set_trajectory(const T *x, const T *y, const T *time)
        {

            for (std::size_t i = 0; i < N_TRAJ; ++i)
            {
                traj_x[i] = x[i];
                traj_y[i] = y[i];
                traj_time[i] = time[i];
            }
        }

        JALANSIM_HOST_DEVICE
        void get_trajectory(T *x, T *y, T *time) const
        {

            for (std::size_t i = 0; i < N_TRAJ; ++i)
            {
                x[i] = traj_x[i];
                y[i] = traj_y[i];
                time[i] = traj_time[i];
            }
        }
    };

}
