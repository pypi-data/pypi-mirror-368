#pragma once
#include <nanobind/nanobind.h>

#include "wrappers/batch_sim.hpp"

namespace nb = nanobind;
using nb::literals::operator""_a;


template <typename T, typename DynamicsModel, typename Collision>
void define_batchsim_class(nb::module_ &m,
                           const std::string &name = "BatchSim")
{
    using Sim = jalansim::Jalansim<T, DynamicsModel, Collision>;

    using Wrapper = BatchSimWrapper<T, Sim>;
    nb::class_<Wrapper>(m, name.c_str(), "A pool of simulators for batch operations")
        .def(nb::init<std::size_t>(),
             "N"_a,
             "Allocate N simulators using default DiffDrive & CircleCollision.")
        .def(nb::init<std::size_t, typename Sim::DynamicsModel, typename Sim::Collision>(),
             "N"_a, "dyn"_a, "col"_a,
             "Allocate N simulators with the given DiffDrive and CircleCollision.")
        .def("set_map", &Wrapper::set_map, "map"_a,
             "Attach a Map to every simulator")
        .def("get_map_single", &Wrapper::get_map_single, "idx"_a,
             "Get the map_t pointer for a single simulator at index idx. "
             "This is useful for accessing the map directly in CUDA kernels.")
        .def("sample_map_from_collection", &Wrapper::sample_map_from_collection,
             "map_collection"_a, "base_seed"_a = 0, "mask"_a = nb::none())
        .def("reset", &Wrapper::reset, "mask"_a = nb::none())
        .def("set_state", &Wrapper::set_state,
             "states"_a, "mask"_a = nb::none(),
             "Write (optionally masked) state matrix")
        .def("get_state", &Wrapper::get_state,
             "out_states"_a,
             "Read (optionally masked) state matrix")
        .def("collided", &Wrapper::collided, "hits"_a,
             "Fill a 1-D CUDA tensor with per-simulator collision flags")
        .def("get_range", &Wrapper::get_range,
             "scan"_a, "beams"_a, "fov"_a, "rmax"_a,
             "Fill the scan tensor with range data")
        .def("step", &Wrapper::step,
             "inputs"_a, "dt"_a,
             "Advance all simulators by dt using inputs of shape [NxINPUT_DIM].");
}
