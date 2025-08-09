#pragma once

#include <cmath>
#include "jalansim/map/map.hpp"
#include "jalansim/cuda_macros.hpp"

namespace jalansim::range
{

    template <typename T = double>
    struct RayMarching
    {
        const T clearance_threshold = T(0.1);

        JALANSIM_HOST_DEVICE
        static T map_calc_range(
            const jalansim::map::Map<T> *map,
            T ox,
            T oy,
            T oa,
            T max_range)
        {
            const T dir_x = std::cos(oa);
            const T dir_y = std::sin(oa);
            T t = T(0);
            const T min_step = map->scale * T(0.1);

            while (t < max_range)
            {
                T x = ox + dir_x * t;
                T y = oy + dir_y * t;

                T gx = map->to_if(x);
                T gy = map->to_jf(y);

                int i = int(std::floor(gx)), j = int(std::floor(gy));

                if (!map->valid(i, j))
                {
                    return max_range;
                }

                T clearance = map->interpolate_dist(gx, gy) - T(0.5) * map->scale;

                if (clearance <= T(0.1))
                {
                    return t;
                }

                T step = clearance * T(0.9);
                if (step < min_step)
                    step = min_step;
                t += step;
            }

            return max_range;
        }
    };

}
