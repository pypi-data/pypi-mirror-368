#pragma once

#include <cmath>
#include "jalansim/map/map.hpp"
#include "jalansim/cuda_macros.hpp"

namespace jalansim::range
{

    template <typename T = double>
    struct Bresenham
    {

        JALANSIM_HOST_DEVICE
        static T map_calc_range(
            const jalansim::map::Map<T> *map,
            T ox,
            T oy,
            T oa,
            T max_range)
        {

            int x0 = map->to_i(ox);
            int y0 = map->to_j(oy);
            int x1 = map->to_i(ox + max_range * std::cos(oa));
            int y1 = map->to_j(oy + max_range * std::sin(oa));

            bool steep = std::abs(y1 - y0) > std::abs(x1 - x0);
            if (steep)
            {

                int tmp = x0;
                x0 = y0;
                y0 = tmp;
                tmp = x1;
                x1 = y1;
                y1 = tmp;
            }

            int deltax = std::abs(x1 - x0);
            int deltay = std::abs(y1 - y0);
            int error = 0;
            int deltaerr = deltay;
            int x = x0;
            int y = y0;
            int xstep = (x0 < x1) ? 1 : -1;
            int ystep = (y0 < y1) ? 1 : -1;

            auto report_hit = [&](int cx, int cy)
            {
                T dx = T(cx - x0);
                T dy = T(cy - y0);
                return std::sqrt(dx * dx + dy * dy) * map->scale;
            };

            if (steep)
            {

                if (map->is_valid(y, x) &&

                    map->cells[map->index(y, x)].occupancy > -1)
                    return report_hit(x, y);
            }
            else
            {

                if (map->is_valid(x, y) &&

                    map->cells[map->index(x, y)].occupancy > -1)
                    return report_hit(x, y);
            }

            while (x != x1 + xstep)
            {
                x += xstep;
                error += deltaerr;
                if (error * 2 >= deltax)
                {
                    y += ystep;
                    error -= deltax;
                }

                if (steep)
                {

                    if (map->is_valid(y, x) &&

                        map->cells[map->index(y, x)].occupancy > -1)
                        return report_hit(x, y);
                }
                else
                {

                    if (map->is_valid(x, y) &&

                        map->cells[map->index(x, y)].occupancy > -1)
                        return report_hit(x, y);
                }
            }

            return max_range;
        }
    };

}
