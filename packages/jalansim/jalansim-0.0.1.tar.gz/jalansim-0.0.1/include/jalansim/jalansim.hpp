#pragma once
#include <vector>
#include <cmath>

#include "jalansim/cuda_macros.hpp"
#include "jalansim/dynamics/dynamics.hpp"
#include "jalansim/map/map.hpp"
#include "jalansim/collision/collision.hpp"
#include "jalansim/range/range.hpp"

namespace jalansim
{

    template <typename T,
              typename DynamicsModelT,
              typename CollisionT = collision::PolygonCollision<T>,
              typename RangeT = range::Bresenham<T>>
    class Jalansim
    {
    public:
        static constexpr std::size_t STATE_DIM = DynamicsModelT::STATE_DIM;
        static constexpr std::size_t INPUT_DIM = DynamicsModelT::INPUT_DIM;

        using Map = map::Map<T>;
        using Dynamics = dynamics::Dynamics<T, DynamicsModelT>;
        using DynamicsModel = DynamicsModelT;
        using Collision = CollisionT;

        constexpr Jalansim() = default;

        JALANSIM_HOST_DEVICE
        explicit Jalansim(const DynamicsModelT &dm)
            : dyn_(), collision_()
        {
            dyn_.model = dm;
        }

        JALANSIM_HOST_DEVICE
        Jalansim(const DynamicsModelT &dm, const CollisionT &cp)
            : dyn_(), collision_(cp)
        {
            dyn_.model = dm;
        }

        JALANSIM_HOST_DEVICE
        void set_map(Map *m)
        {
            map_ = m;
        }

        JALANSIM_HOST_DEVICE
        Map *get_map()
        {
            return map_;
        }

        JALANSIM_HOST_DEVICE
        Map *get_map() const
        {
            return map_;
        }

        JALANSIM_HOST_DEVICE
        bool collided() const
        {
            return collision_.check(map_, dyn_.get_x(), dyn_.get_y(), dyn_.get_theta());
        }

        JALANSIM_HOST_DEVICE
        bool collided(T x, T y, T theta = T(0.0)) const
        {
            return collision_.check(map_, x, y, theta);
        }

        JALANSIM_HOST_DEVICE
        void step(const T *u, T dt,
                  dynamics::Scheme scheme = dynamics::Scheme::Euler)
        {
            dyn_.step(u, dt, scheme);
        }

        JALANSIM_HOST_DEVICE
        void reset()
        {
            dyn_.reset();
        }

        JALANSIM_HOST_DEVICE
        T get_range_single(
            int num_beams,
            T fov,
            T max_range,
            int beam_idx) const
        {
            T ox = dyn_.get_x();
            T oy = dyn_.get_y();
            T theta0 = dyn_.get_theta();

            if (num_beams <= 1)
            {
                return RangeT::map_calc_range(map_, ox, oy, theta0, max_range);
            }

            T start = theta0 - fov * T(0.5);
            T step = fov / T(num_beams - 1);
            T angle = start + step * T(beam_idx);

            return RangeT::map_calc_range(map_, ox, oy, angle, max_range);
        }

        std::vector<T> get_range(
            int num_beams,
            T fov,
            T max_range) const
        {
            std::vector<T> ranges;
            ranges.reserve(num_beams);

            for (int i = 0; i < num_beams; ++i)
            {
                ranges.push_back(
                    get_range_single(num_beams, fov, max_range, i));
            }

            return ranges;
        }

        JALANSIM_HOST_DEVICE
        T *get_state() { return dyn_.x; }
        JALANSIM_HOST_DEVICE
        const T *get_state() const { return dyn_.x; }

        JALANSIM_HOST_DEVICE
        void set_state(const T *state)
        {
            for (std::size_t i = 0; i < STATE_DIM; ++i)
            {
                dyn_.x[i] = state[i];
            }
        }

        JALANSIM_HOST_DEVICE
        Dynamics &dynamics() { return dyn_; }
        JALANSIM_HOST_DEVICE
        const Dynamics &dynamics() const { return dyn_; }

    private:
        Map *map_{nullptr};
        Dynamics dyn_{};
        CollisionT collision_;
    };

}
