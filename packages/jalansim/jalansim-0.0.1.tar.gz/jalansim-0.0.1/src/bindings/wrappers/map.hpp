#pragma once
#include <jalansim/map/map.hpp>

template<typename T>
struct MapWrapper {
    using MapT = jalansim::map::Map<T>;
    MapT *ptr;
    bool owns_ptr_;

    explicit MapWrapper(MapT *m, bool owns = true) : ptr(m), owns_ptr_(owns) {}

    void update_dist(double max_d = 10.0) {
        ptr->update_dist(max_d);
    }

    std::vector<std::vector<int8_t>> get_occupancy() const {
        int W = ptr->size_x;
        int H = ptr->size_y;
        std::vector<std::vector<int8_t>> states(H, std::vector<int8_t>(W));
        for (int j = 0; j < H; ++j) {
            for (int i = 0; i < W; ++i) {
                int idx = ptr->index(i, j);
                states[j][i] = ptr->cells[idx].occupancy;
            }
        }
        return states;
    }

    std::vector<std::vector<float>> get_dist() const {
        int W = ptr->size_x;
        int H = ptr->size_y;
        std::vector<std::vector<float>> dists(H, std::vector<float>(W));
        for (int j = 0; j < H; ++j) {
            for (int i = 0; i < W; ++i) {
                int idx = ptr->index(i, j);
                dists[j][i] = ptr->cells[idx].dist;
            }
        }
        return dists;
    }

    int width()  const { return ptr->size_x; }
    int height() const { return ptr->size_y; }
    double scale() const { return ptr->scale; }
    bool managed() const { return ptr->cells_managed; }

    MapT *raw() const { return ptr; }
};