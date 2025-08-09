#pragma once
#include <cstddef>
#include <cmath>
#include "jalansim/map/map.hpp"
#include "jalansim/cuda_macros.hpp"

namespace jalansim::collision
{
    template <typename T>
    struct PolygonCollision
    {
        T poly_x[16];
        T poly_y[16];
        std::size_t verts = 4;

        JALANSIM_HOST_DEVICE
        bool check(
            const jalansim::map::Map<T> *map,
            T cx, T cy, T theta) const
        {
            T s = std::sin(theta), c = std::cos(theta);
            T margin = T(0.5) * map->scale;

            for (std::size_t j = 0, k = verts - 1; j < verts; k = j++)
            {

                T wx = cx + c * poly_x[j] - s * poly_y[j];
                T wy = cy + s * poly_x[j] + c * poly_y[j];
                T d = map->interpolate_dist(
                    map->to_if(wx),
                    map->to_jf(wy));
                if (d <= margin)
                    return true;

                T mx = T(0.5) * (poly_x[j] + poly_x[k]);
                T my = T(0.5) * (poly_y[j] + poly_y[k]);
                wx = cx + c * mx - s * my;
                wy = cy + s * mx + c * my;
                d = map->interpolate_dist(
                    map->to_if(wx),
                    map->to_jf(wy));
                if (d <= margin)
                    return true;
            }
            return false;
        }

        JALANSIM_HOST_DEVICE
        void set_polygon(const T *x, const T *y, std::size_t n)
        {
            if (n > 16)
            {

                printf("PolygonCollision: Maximum 16 vertices allowed, got %zu.\n", n);
                return;
            }
            if (n < 3)
            {

                printf("PolygonCollision: At least 3 vertices required, got %zu.\n", n);
                return;
            }
            verts = n;
            for (std::size_t i = 0; i < n; ++i)
            {
                poly_x[i] = x[i];
                poly_y[i] = y[i];
            }
        }

        JALANSIM_HOST_DEVICE
        std::size_t get_num_verts() const
        {
            return verts;
        }

        JALANSIM_HOST_DEVICE
        void get_polygon(T *x, T *y) const
        {
            for (std::size_t i = 0; i < verts; ++i)
            {
                x[i] = poly_x[i];
                y[i] = poly_y[i];
            }
        }
    };

}
