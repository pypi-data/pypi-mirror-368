#pragma once

#include "jalansim/cuda_macros.hpp"
#include "jalansim/map/map.hpp"

#include <cstdlib>
#include <ctime>
#include <cstddef>

namespace jalansim::map
{

    namespace collection
    {
        JALANSIM_HOST_DEVICE unsigned int xorshift_rand(unsigned int &seed)
        {
            seed ^= seed << 13;
            seed ^= seed >> 17;
            seed ^= seed << 5;
            return seed;
        }
    }

    template <typename T>
    class MapCollection
    {
    private:
        Map<T> **maps_storage_;
        int num_maps_;
        int capacity_;

    public:
        explicit MapCollection(int initial_capacity = 10) : maps_storage_(nullptr),
                                                            num_maps_(0),
                                                            capacity_(initial_capacity > 0 ? initial_capacity : 1)
        {
            std::size_t size_bytes = static_cast<std::size_t>(capacity_) * sizeof(Map<T> *);

            if (capacity_ <= 0)
            {
                maps_storage_ = nullptr;
                capacity_ = 0;
                num_maps_ = 0;
                return;
            }

#if JALANSIM_CUDA_ENABLED
            cudaMallocManaged(reinterpret_cast<void **>(&maps_storage_), size_bytes);
            if (!maps_storage_)
            {
                capacity_ = 0;
                num_maps_ = 0;
            }
#else
            maps_storage_ = static_cast<Map<T> **>(std::malloc(size_bytes));
            if (!maps_storage_)
            {
                capacity_ = 0;
                num_maps_ = 0;
            }
            std::srand(static_cast<unsigned int>(std::time(nullptr)));
#endif
        }

        ~MapCollection()
        {
            if (maps_storage_)
            {
#if JALANSIM_CUDA_ENABLED
                cudaFree(maps_storage_);
#else
                std::free(maps_storage_);
#endif
                maps_storage_ = nullptr;
            }
            num_maps_ = 0;
            capacity_ = 0;
        }

        MapCollection(const MapCollection &) = delete;
        MapCollection &operator=(const MapCollection &) = delete;

        JALANSIM_HOST_DEVICE
        void add_map(Map<T> *map_to_add)
        {
            if (!map_to_add)
                return;

            if (num_maps_ < capacity_)
            {
                maps_storage_[num_maps_] = map_to_add;
                num_maps_++;
            }
        }

        JALANSIM_HOST_DEVICE
        Map<T> *get(int idx) const
        {
            if (maps_storage_ && idx >= 0 && idx < num_maps_)
            {
                return maps_storage_[idx];
            }
            return nullptr;
        }

        JALANSIM_HOST_DEVICE
        Map<T> *sample(unsigned int &rng_seed)
        {
            if (num_maps_ == 0 || !maps_storage_)
            {
                return nullptr;
            }
            int random_idx = collection::xorshift_rand(rng_seed) % num_maps_;
            return maps_storage_[random_idx];
        }

#if !JALANSIM_CUDA_ENABLED
        Map<T> *sample()
        {
            if (num_maps_ == 0 || !maps_storage_)
            {
                return nullptr;
            }
            int random_idx = std::rand() % num_maps_;
            return maps_storage_[random_idx];
        }
#endif

        JALANSIM_HOST_DEVICE int get_count() const { return num_maps_; }
        JALANSIM_HOST_DEVICE int get_capacity() const { return capacity_; }
    };

}
