#pragma once
#include <nanobind/nanobind.h>
#include "jalansim/dynamics/models/bicycle.hpp"

namespace nb = nanobind;

template <typename T>
void define_bicycle_class(nb::module_ &m) {
    using namespace jalansim::dynamics::models;

    nb::class_<Bicycle<T>>(m, "Bicycle", "Kinematic bicycle (single-track) model")
        .def(nb::init<>())
        .def_rw("a", &Bicycle<T>::a,
            "Distance from CoG to front axle (m)")
        .def_rw("b", &Bicycle<T>::b,
            "Distance from CoG to rear axle (m)")
        .def_rw("delta_min", &Bicycle<T>::delta_min,
            "Minimum steering angle (rad)")
        .def_rw("delta_max", &Bicycle<T>::delta_max,
            "Maximum steering angle (rad)")
        .def_rw("delta_dot_min", &Bicycle<T>::delta_dot_min,
            "Minimum steering rate (rad/s)")
        .def_rw("delta_dot_max", &Bicycle<T>::delta_dot_max,
            "Maximum steering rate (rad/s)")
        .def_rw("v_min", &Bicycle<T>::v_min,
            "Minimum velocity (m/s)")
        .def_rw("v_max", &Bicycle<T>::v_max,
            "Maximum velocity (m/s)")
        .def_rw("acc_min", &Bicycle<T>::acc_min,
            "Minimum acceleration (m/s²)")
        .def_rw("acc_max", &Bicycle<T>::acc_max,
            "Maximum acceleration (m/s²)")
        .def("rhs", &Bicycle<T>::rhs,
            "Compute right-hand side of dynamics")
        .def("reset", &Bicycle<T>::reset,
            "Reset internal state")
        ;
}