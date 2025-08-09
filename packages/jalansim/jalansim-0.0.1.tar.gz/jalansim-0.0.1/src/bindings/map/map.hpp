#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>

#include <jalansim/map/map_loader.hpp>

#include "../wrappers/map.hpp"

namespace nb = nanobind;
using nb::literals::operator""_a;

template <typename T>
void define_map_class(nb::module_ &m)
{
    using MapWrapperT = MapWrapper<T>;
    nb::class_<MapWrapperT>(m, "Map", "Occupancy/CSpace grid")
        .def_static("load_image", [](const std::string &path, T resolution, T origin_x, T origin_y, T yaw, bool negate = false, T occ_th = 0.65, T free_th = 0.196, int padding = 0, int padding_val = 0)
                    {
                auto *mp = jalansim::map::load_image<T>(
                    path, resolution, origin_x, origin_y, yaw,
                    negate, occ_th, free_th, padding, padding_val);
                return new MapWrapperT(mp); }, "path"_a, "resolution"_a, "origin_x"_a, "origin_y"_a, "yaw"_a, "negate"_a = false, "occ_th"_a = 0.65, "free_th"_a = 0.196, "padding"_a = 0, "padding_val"_a = 0, nb::rv_policy::take_ownership, "Load a PGM/PNG and return a ready-to-use Map object")
        .def("update_dist", &MapWrapperT::update_dist, "max_d"_a = 10.0, "Recompute the configuration-space distance field.")
        .def("get_occupancy", &MapWrapperT::get_occupancy, "Return a nested list of occ_state values (H×W).")
        .def("get_dist", &MapWrapperT::get_dist, "Return a nested list of occ_dist values (H×W).")
        .def("width", &MapWrapperT::width)
        .def("height", &MapWrapperT::height)
        .def("scale", &MapWrapperT::scale)
        .def("managed", &MapWrapperT::managed, "True if cells are in unified memory (CUDA) or not.");
}