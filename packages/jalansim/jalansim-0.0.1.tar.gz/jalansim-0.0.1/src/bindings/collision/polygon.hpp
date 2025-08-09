#pragma once
#include <nanobind/nanobind.h>
#include <nanobind/stl/vector.h>
#include "jalansim/collision/polygon.hpp"

namespace nb = nanobind;

template <typename T>
void define_polygoncollision_class(nb::module_ &m)
{
    using namespace jalansim::collision;

    nb::class_<PolygonCollision<T>>(m, "Polygon", "Convex-polygon robot collision policy")
        .def(nb::init<>())
        .def("set_polygon", [](PolygonCollision<T> &self, const std::vector<T> &x_coords, const std::vector<T> &y_coords)
             {
            if (x_coords.size() != y_coords.size()) {
                throw std::runtime_error("x and y coordinate lists must have same length");
            }
            if (x_coords.size() > 4) {
                throw std::runtime_error("maximum 4 vertices supported");
            }
            if (x_coords.empty()) {
                throw std::runtime_error("polygon must have at least 1 vertex");
            }
            self.set_polygon(x_coords.data(), y_coords.data(), x_coords.size()); }, "Set polygon vertices from x,y coordinate lists")
        .def("get_polygon", [](const PolygonCollision<T> &self)
             {
            std::vector<T> x_coords(self.verts);
            std::vector<T> y_coords(self.verts);
            self.get_polygon(x_coords.data(), y_coords.data());
            return std::make_tuple(x_coords, y_coords); }, "Get polygon vertices as (x_coords, y_coords) tuple")
        .def("check", &PolygonCollision<T>::check, "Check for collision at given pose (x, y, theta)");
}
