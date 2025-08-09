#pragma once
#include <nanobind/nanobind.h>
#include "jalansim/dynamics/models/diff_drive.hpp"

namespace nb = nanobind;

template <typename T>
void define_diff_drive_class(nb::module_ &m) {
    using namespace jalansim::dynamics::models;

    nb::class_<DiffDrive<T>>(m, "DiffDrive", "Unicycle-like differential drive model")
        .def(nb::init<>())
        .def_rw("wheel_r", &DiffDrive<T>::wheel_r,
            "Wheel radius (m)")
        .def_rw("wheel_b", &DiffDrive<T>::wheel_b,
            "Distance between wheels (m)")
        .def_rw("vmin", &DiffDrive<T>::vmin,
            "Minimum linear velocity")
        .def_rw("vmax", &DiffDrive<T>::vmax,
            "Maximum linear velocity")
        .def_rw("wmin", &DiffDrive<T>::wmin,
            "Minimum angular velocity")
        .def_rw("wmax", &DiffDrive<T>::wmax,
            "Maximum angular velocity")
        ;
}
