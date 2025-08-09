#pragma once
#include <nanobind/nanobind.h>

#include <jalansim/cuda_macros.hpp>
#include <jalansim/map/map.hpp>

#include "map.hpp"

namespace nb = nanobind;

template<typename T>
struct MapCollectionWrapper {
    using MapT = jalansim::map::Map<T>;
    using MapCollectionT = jalansim::map::MapCollection<T>;
    using MapWrapperT = MapWrapper<T>;
    MapCollectionT* collection_ptr_;

    explicit MapCollectionWrapper(int initial_capacity = 10) : collection_ptr_(nullptr) {
#if JALANSIM_CUDA_ENABLED
        cudaMallocManaged(reinterpret_cast<void**>(&collection_ptr_), sizeof(MapCollectionT));
#else
        collection_ptr_ = static_cast<MapCollectionT*>(std::malloc(sizeof(MapCollectionT)));
#endif
        new (collection_ptr_) MapCollectionT(initial_capacity);

        if (collection_ptr_->get_capacity() == 0 && initial_capacity > 0) {
            collection_ptr_->~MapCollection(); 
#if JALANSIM_CUDA_ENABLED
            cudaFree(collection_ptr_);
#else
            free(collection_ptr_);
#endif
            collection_ptr_ = nullptr; 
            throw std::runtime_error("MapCollection internal initialization failed for capacity " + std::to_string(initial_capacity));
        }
    }


    MapCollectionWrapper(const MapCollectionWrapper&) = delete;
    MapCollectionWrapper& operator=(const MapCollectionWrapper&) = delete;

    void add_map(MapWrapperT& map_w) {
        if (!collection_ptr_) throw std::runtime_error("MapCollection not initialized");
        if (!map_w.raw()) throw std::runtime_error("Cannot add a null map from MapWrapper");
        collection_ptr_->add_map(map_w.raw());
    }

    MapWrapperT get(int idx) {
        if (!collection_ptr_) throw std::runtime_error("MapCollection not initialized");
        MapT* m = collection_ptr_->get(idx);
        return MapWrapperT(m, false);
    }

    nb::tuple sample(unsigned int seed_val) {
        if (!collection_ptr_) throw std::runtime_error("MapCollection not initialized");
        unsigned int current_seed = seed_val;
        MapT* m = collection_ptr_->sample(current_seed);
        return nb::make_tuple(MapWrapper(m, false), current_seed);
    }

    int get_count() const {
        if (!collection_ptr_) return 0;
        return collection_ptr_->get_count();
    }

    int get_capacity() const {
        if (!collection_ptr_) return 0;
        return collection_ptr_->get_capacity();
    }
    
    MapCollectionT* raw() const { return collection_ptr_; }
};
