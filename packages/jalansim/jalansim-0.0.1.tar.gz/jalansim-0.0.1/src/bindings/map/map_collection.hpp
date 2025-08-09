#include <nanobind/nanobind.h>

#include "../wrappers/map_collection.hpp"

namespace nb = nanobind;
using nb::literals::operator""_a;

template <typename T>
void define_map_collection_class(nb::module_ &m)
{
    using MapCollectionWrapperT = MapCollectionWrapper<T>;
    nb::class_<MapCollectionWrapperT>(m, "MapCollection", "A collection of maps with fixed capacity")
        .def(nb::init<int>(), "initial_capacity"_a = 10)
        .def("add_map", &MapCollectionWrapperT::add_map, "map"_a,
             "Adds a map (non-owning reference) to the collection. The caller must ensure the original MapWrapper (and its map_t) outlives its use by this collection if the MapWrapper is temporary.")
        .def("get", &MapCollectionWrapperT::get, "idx"_a,
             "Returns a non-owning MapWrapper for the map at the given index.")
        .def("sample", &MapCollectionWrapperT::sample, "seed"_a,
             "Samples a map using a given seed. Returns a tuple (MapWrapper, updated_seed). The MapWrapper is non-owning.")
        .def("get_count", &MapCollectionWrapperT::get_count)
        .def("get_capacity", &MapCollectionWrapperT::get_capacity);
}
