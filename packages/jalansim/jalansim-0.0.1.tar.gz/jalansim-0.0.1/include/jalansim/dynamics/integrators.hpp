#pragma once
#include <cstddef>
#include "jalansim/cuda_macros.hpp"

namespace jalansim::dynamics::integrators
{

    template <typename T, class Model>
    JALANSIM_HOST_DEVICE void euler(T *x, const T *u, T dt, Model &m)
    {
        T k[Model::STATE_DIM];
        m.rhs(x, u, k, dt);
        for (std::size_t i = 0; i < Model::STATE_DIM; ++i)
            x[i] += dt * k[i];
    }

    template <typename T, class Model>
    JALANSIM_HOST_DEVICE void rk4(T *x, const T *u, T dt, Model &m)
    {
        T k1[Model::STATE_DIM], k2[Model::STATE_DIM], k3[Model::STATE_DIM], k4[Model::STATE_DIM], tmp[Model::STATE_DIM];

        m.rhs(x, u, k1, dt);

        for (std::size_t i = 0; i < Model::STATE_DIM; ++i)
            tmp[i] = x[i] + T(0.5) * dt * k1[i];
        Model m2 = m;
        m2.rhs(tmp, u, k2, dt);

        for (std::size_t i = 0; i < Model::STATE_DIM; ++i)
            tmp[i] = x[i] + T(0.5) * dt * k2[i];
        Model m3 = m;
        m3.rhs(tmp, u, k3, dt);

        for (std::size_t i = 0; i < Model::STATE_DIM; ++i)
            tmp[i] = x[i] + dt * k3[i];
        Model m4 = m;
        m4.rhs(tmp, u, k4, dt);

        for (std::size_t i = 0; i < Model::STATE_DIM; ++i)
            x[i] += dt * (k1[i] + T(2) * k2[i] + T(2) * k3[i] + k4[i]) / T(6);
    }

}
