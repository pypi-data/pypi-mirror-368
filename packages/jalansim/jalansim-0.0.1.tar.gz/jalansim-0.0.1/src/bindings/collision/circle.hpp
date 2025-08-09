#pragma once
#include <nanobind/nanobind.h>
#include "jalansim/collision/circle.hpp"

namespace nb = nanobind;

template <typename T>
void define_circlecollision_class(nb::module_ &m)
{
    using namespace jalansim::collision;

    nb::class_<CircleCollision<T>>(m, "Circle", "Circular-robot collision policy")
        .def(nb::init<>())
        .def("set_radius", &CircleCollision<T>::set_radius,
             "Set the robot radius (m) used in collision check",
             "radius"_a)
        .def_rw("radius", &CircleCollision<T>::radius,
                "Robot radius (m) used in collision check");
}
