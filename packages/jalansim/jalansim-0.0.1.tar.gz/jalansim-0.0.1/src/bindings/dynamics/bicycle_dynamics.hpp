#pragma once
#include <nanobind/nanobind.h>
#include "jalansim/dynamics/models/bicycle_dynamics.hpp"

namespace nb = nanobind;

template <typename T>
void define_bicycle_dynamics_class(nb::module_ &m) {
    using namespace jalansim::dynamics::models;

    nb::class_<BicycleDynamics<T>>(m, "BicycleDynamics", "Dynamic bicycle (single-track) model")
        .def(nb::init<>())
        .def_rw("a", &BicycleDynamics<T>::a,
            "Distance from CoG to front axle (m)")
        .def_rw("b", &BicycleDynamics<T>::b,
            "Distance from CoG to rear axle (m)")
        .def_rw("h", &BicycleDynamics<T>::h,
            "CoM height (m)")
        .def_rw("m", &BicycleDynamics<T>::m,
            "Vehicle mass (kg)")
        .def_rw("I_z", &BicycleDynamics<T>::I_z,
            "Moment of inertia (kg·m²)")
        .def_rw("mu", &BicycleDynamics<T>::mu,
            "surface friction coefficient")
        .def_rw("C_Sf", &BicycleDynamics<T>::C_Sf,
            "Front tire cornering stiffness (N/rad)")
        .def_rw("C_Sr", &BicycleDynamics<T>::C_Sr,
            "Rear tire cornering stiffness (N/rad)")
        .def_rw("delta_min", &BicycleDynamics<T>::delta_min,
            "Minimum steering angle (rad)")
        .def_rw("delta_max", &BicycleDynamics<T>::delta_max,
            "Maximum steering angle (rad)")
        .def_rw("delta_dot_min", &BicycleDynamics<T>::delta_dot_min,
            "Minimum steering rate (rad/s)")
        .def_rw("delta_dot_max", &BicycleDynamics<T>::delta_dot_max,
            "Maximum steering rate (rad/s)")
        .def_rw("acc_min", &BicycleDynamics<T>::acc_min,
            "Minimum acceleration (m/s²)")
        .def_rw("acc_max", &BicycleDynamics<T>::acc_max,
            "Maximum acceleration (m/s²)")
        .def("rhs", &BicycleDynamics<T>::rhs,
            "Compute right-hand side of dynamics")
        .def("reset", &BicycleDynamics<T>::reset,
            "Reset internal state")
        ;
}