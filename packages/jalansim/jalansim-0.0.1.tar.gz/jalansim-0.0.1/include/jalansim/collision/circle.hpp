#pragma once
#include "jalansim/map/map.hpp"
#include "jalansim/cuda_macros.hpp"

namespace jalansim::collision
{
    template <typename T>
    struct CircleCollision
    {
        T radius = T(0.1);

        JALANSIM_HOST_DEVICE
        bool check(
            const jalansim::map::Map<T> *m,
            T x, T y, T theta = T(0.0)) const
        {

            T gi = m->to_if(x);
            T gj = m->to_jf(y);

            T dist = m->interpolate_dist(gi, gj);

            T clearance = dist - T(0.5) * m->scale;
            return (clearance <= radius);
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
    };

}
