#pragma once
#include <iterator>
#include "jalansim/dynamics/integrators.hpp"

namespace jalansim::dynamics
{

    enum class Scheme
    {
        Euler,
        RK4
    };

    template <typename T, class Model>
    class Dynamics
    {
    public:
        static constexpr std::size_t STATE_DIM = Model::STATE_DIM;
        static constexpr std::size_t INPUT_DIM = Model::INPUT_DIM;

        Model model;
        T x[STATE_DIM]{};

        JALANSIM_HOST_DEVICE T get_x() const { return x[0]; }
        JALANSIM_HOST_DEVICE T get_y() const { return x[1]; }
        JALANSIM_HOST_DEVICE T get_theta() const { return x[2]; }

        JALANSIM_HOST_DEVICE
        void step(const T *u, T dt, Scheme s = Scheme::RK4)
        {
            if (s == Scheme::Euler)
                integrators::euler<T, Model>(x, u, dt, model);
            else
                integrators::rk4<T, Model>(x, u, dt, model);
        }

        JALANSIM_HOST_DEVICE
        void reset()
        {

            for (std::size_t i = 0; i < STATE_DIM; ++i)
            {
                x[i] = T(0);
            }
            model.reset();
        }
    };

}
