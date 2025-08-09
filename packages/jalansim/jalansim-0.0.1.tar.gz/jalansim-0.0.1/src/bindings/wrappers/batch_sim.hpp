#pragma once
#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>

#include <jalansim/cuda_macros.hpp>
#include <jalansim/jalansim.hpp>
#include <jalansim/batch/batch.hpp>

#include "map.hpp"
#include "map_collection.hpp"

namespace nb = nanobind;

#if JALANSIM_CUDA_ENABLED
    #ifndef NB_DEVICE
    #define NB_DEVICE nb::device::cuda
    #endif
#else
    #ifndef NB_DEVICE
    #define NB_DEVICE nb::device::cpu
    #endif
#endif

template <typename T, typename Sim>
struct BatchSimWrapper
{
    using MapWrapperT = MapWrapper<T>;
    using MapCollectionWrapperT = MapCollectionWrapper<T>;
    std::size_t n;
    Sim *ptr;

    explicit BatchSimWrapper(std::size_t N)
        : n(N)
    {
        typename Sim::DynamicsModel dyn;
        typename Sim::Collision col;
#if JALANSIM_CUDA_ENABLED
        cudaMallocManaged(&ptr, N * sizeof(Sim));
#else
        ptr = (Sim *)std::malloc(N * sizeof(Sim));
        if (!ptr)
            throw std::runtime_error("Failed to allocate memory for SimPool");
#endif
        jalansim::batch::init<Sim>(ptr, dyn, col, N);
#if JALANSIM_CUDA_ENABLED
        check_cuda("BatchSimWrapper(default)");
#endif
    }

    explicit BatchSimWrapper(std::size_t N,
                            const typename Sim::DynamicsModel &dyn,
                            const typename Sim::Collision &col)
        : n(N)
    {
#if JALANSIM_CUDA_ENABLED
        cudaMallocManaged(&ptr, N * sizeof(Sim));
#else
        ptr = (Sim *)std::malloc(N * sizeof(Sim));
        if (!ptr)
            throw std::runtime_error("Failed to allocate memory for SimPool");
#endif
        jalansim::batch::init<Sim>(ptr, dyn, col, N);
#if JALANSIM_CUDA_ENABLED
        check_cuda("BatchSimWrapper(custom)");
#endif
    }

    void set_map(const MapWrapperT &map)
    {
        jalansim::batch::set_map<T, Sim>(ptr, map.raw(), n);
#if JALANSIM_CUDA_ENABLED
        check_cuda("set_map");
#endif
    }

    MapWrapperT get_map_single(const int idx)
    {
        auto *m = ptr[idx].get_map()->clone();
        return MapWrapperT(m, false);
    }

    void sample_map_from_collection(MapCollectionWrapperT &mcw,
                                    unsigned int base_seed = 0,
                                    nb::handle mask_obj = nb::none())
    {
        if (!ptr)
            throw std::runtime_error("SimPool not initialized in sample_map_from_collection");
        if (!mcw.raw())
            throw std::runtime_error("MapCollectionWrapper is not valid for sampling in sample_map_from_collection");

        const bool *mask_ptr = nullptr;
        nb::ndarray<bool, nb::ndim<1>, NB_DEVICE> mask_array_holder;

        if (!mask_obj.is_none())
        {
            mask_array_holder = nb::cast<nb::ndarray<bool, nb::ndim<1>, NB_DEVICE>>(mask_obj);
            if (mask_array_holder.shape(0) != n)
                throw std::runtime_error("mask length mismatch in sample_map_from_collection. Expected " +
                                         std::to_string(n) + ", got " + std::to_string(mask_array_holder.shape(0)));
            mask_ptr = mask_array_holder.data();
        }

        jalansim::batch::sample_map<T, Sim>(ptr, mcw.raw(), n, base_seed, mask_ptr);
#if JALANSIM_CUDA_ENABLED
        check_cuda("sample_map_from_collection");
#endif
    }

    void set_state(nb::ndarray<T, nb::ndim<2>, NB_DEVICE> states,
                   nb::handle mask_obj = nb::none())
    {
        constexpr std::size_t D = Sim::STATE_DIM;
        if (states.shape(0) != n || states.shape(1) != D)
            throw std::runtime_error("states must be (" +
                                     std::to_string(n) + "," +
                                     std::to_string(D) + ")");
        const bool *mask_ptr = nullptr;
        if (!mask_obj.is_none())
        {
            auto mask = nb::cast<
                nb::ndarray<bool, nb::ndim<1>, NB_DEVICE>>(mask_obj);
            if (mask.shape(0) != n)
                throw std::runtime_error("mask length mismatch");
            mask_ptr = mask.data();
        }
        jalansim::batch::set_state<T, Sim>(ptr, states.data(), n, mask_ptr);
#if JALANSIM_CUDA_ENABLED
        check_cuda("set_state");
#endif
    }

    void get_range(nb::ndarray<T, nb::ndim<2>, NB_DEVICE> scan,
                   int beams, T fov, T rmax)
    {
        if (scan.shape(0) != n || scan.shape(1) != beams)
            throw std::runtime_error("scan must be (" +
                                     std::to_string(n) + "," +
                                     std::to_string(beams) + ")");
        jalansim::batch::get_range<T, Sim>(ptr, scan.data(), beams, fov, rmax, n);
#if JALANSIM_CUDA_ENABLED
        check_cuda("get_range");
#endif
    }

    void reset(nb::handle mask_obj = nb::none())
    {
        const bool *mask_ptr = nullptr;
        if (!mask_obj.is_none())
        {
            auto mask = nb::cast<
                nb::ndarray<bool, nb::ndim<1>, NB_DEVICE>>(mask_obj);
            if (mask.shape(0) != n)
                throw std::runtime_error("mask must have length " +
                                         std::to_string(n));
            mask_ptr = mask.data();
        }
        jalansim::batch::reset<T, Sim>(ptr, n, mask_ptr);
#if JALANSIM_CUDA_ENABLED
        check_cuda("reset");
#endif
    }

    void collided(nb::ndarray<bool, nb::ndim<1>, NB_DEVICE> hits)
    {
        if (hits.shape(0) != n)
            throw std::runtime_error("hits length mismatch");
        jalansim::batch::collided<Sim>(ptr, hits.data(), n);
#if JALANSIM_CUDA_ENABLED
        check_cuda("collided");
#endif
    }

    void step(nb::ndarray<T, nb::ndim<2>, NB_DEVICE> inputs, T dt)
    {
        constexpr std::size_t I = Sim::INPUT_DIM;
        if (inputs.shape(0) != n || inputs.shape(1) != I)
            throw std::runtime_error("step: inputs must have shape (" +
                                     std::to_string(n) + "," +
                                     std::to_string(I) + ")");
        jalansim::batch::step<T, Sim>(ptr, inputs.data(), dt, n);
#if JALANSIM_CUDA_ENABLED
        check_cuda("step");
#endif
    }

    void get_state(nb::ndarray<T, nb::ndim<2>, NB_DEVICE> out_states)
    {
        constexpr std::size_t D = Sim::STATE_DIM;
        if (out_states.shape(0) != n || out_states.shape(1) != D)
            throw std::runtime_error("get_state: out_states must have shape (" +
                                     std::to_string(n) + "," +
                                     std::to_string(D) + ")");
        jalansim::batch::get_state<T, Sim>(ptr, out_states.data(), n);
#if JALANSIM_CUDA_ENABLED
        check_cuda("get_state");
#endif
    }
};
