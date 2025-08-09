#pragma once
#include "jalansim/cuda_macros.hpp"

namespace jalansim::obstacle
{
    template <typename T>
    struct CircleObstacle
    {
        T poly_x[16];
        T poly_y[16];
        std::size_t verts = 4;

        T traj_x[64];
        T traj_y[64];
        T traj_yaw[64];
        T traj_time[64];
        std::size_t traj_size = 1;

        JALANSIM_HOST_DEVICE
        bool collided(T x, T y) const
        {
        }

        JALANSIM_HOST_DEVICE
        T distance(T x, T y) const
        {
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
        void set_trajectory(const T *x, const T *y, const T *yaw, const T *time, std::size_t n)
        {
            if (n > 64)
            {

                printf("CircleObstacle: Maximum 64 trajectory points allowed, got %zu.\n", n);
                return;
            }
            traj_size = n;

            for (std::size_t i = 0; i < traj_size; ++i)
            {
                traj_x[i] = x[i];
                traj_y[i] = y[i];
                traj_yaw[i] = yaw[i];
                traj_time[i] = time[i];
            }
        }

        JALANSIM_HOST_DEVICE
        void get_trajectory(T *x, T *y, T *yaw, T *time) const
        {

            for (std::size_t i = 0; i < traj_size; ++i)
            {
                x[i] = traj_x[i];
                y[i] = traj_y[i];
                yaw[i] = traj_yaw[i];
                time[i] = traj_time[i];
            }
        }
    };

}
