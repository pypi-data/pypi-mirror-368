#include <iostream>
#include <vector>
#include <cmath>

#include "jalansim/jalansim.hpp"
#include "jalansim/dynamics/models/diff_drive.hpp"
#include "jalansim/map/map.hpp"
#include "jalansim/map/map_loader.hpp"
#include "jalansim/collision/collision.hpp"
#include "jalansim/batch/batch.hpp"

using T = float;

using DynamicsModel = jalansim::dynamics::models::DiffDrive<T>;
using Collision     = jalansim::collision::CircleCollision<T>;
using Range         = jalansim::range::Bresenham<T>;
using Sim           = jalansim::Jalansim<T, DynamicsModel, Collision, Range>;

int main() {
    auto* map = jalansim::map::load_image<T>("map_pgm_0.pgm", 0.15, -2.175, -4.875, 0.0);
    if (!map) {
        std::cerr << "Failed to load map\n";
        return -1;
    }
    // map_update_cspace(map, 10.0);
    map->update_dist(10.0);  // Update distance transform

    // 2) Dynamics & collision params
    DynamicsModel dyn_params;
    Collision collision_params;
    collision_params.radius = 0.75;

    // 3) Build batch of sims
    constexpr std::size_t N = 100000;
    std::vector<Sim> sims; 
    sims.reserve(N);
    for (std::size_t i = 0; i < N; ++i) {
        sims.emplace_back(dyn_params, collision_params);
    }

    jalansim::batch::set_map(sims.data(), map, N);

    // 4) Control inputs
    std::vector<T> inputs(N * DynamicsModel::INPUT_DIM);
    for (std::size_t i = 0; i < N; ++i) {
        inputs[i * DynamicsModel::INPUT_DIM]     = 0.8;  // previously tau_r
        inputs[i * DynamicsModel::INPUT_DIM + 1] = 0.0;  // previously tau_l
    }


    // 5) Prepare LIDAR parameters
    const int    num_beams = 720;
    const T fov       = 1.5 * M_PI;   // full 360°
    const T max_range = 10.0;         // meters
    // one big flat array of size N * num_beams
    std::vector<T> ranges(N * num_beams);

    // 6) Reset & simulate, printing LIDAR shape each step
    jalansim::batch::reset<T, Sim>(sims.data(), N);

    for (int step = 0; step < 100; ++step) {
        // advance dynamics
        jalansim::batch::step<T, Sim>(
            sims.data(),
            inputs.data(),
            0.1,  // dt
            N
        );

        // run LIDAR in batch: writes into ranges[0 .. N*num_beams-1]
        jalansim::batch::get_range<T, Sim>(
            sims.data(),
            ranges.data(),
            num_beams,
            fov,
            max_range,
            N
        );

        bool hit0 = sims[0].collided();

        // print the shape (N, num_beams)
        std::printf(
            "Step %d — hit[0] = %s, "
            "ranges[0][0] = %.3f, ranges[0][%d] = %.3f, ranges[0][%d] = %.3f\n",
            step,
            hit0 ? "YES" : "no",
            ranges[0],
            num_beams / 2, ranges[num_beams / 2],
            num_beams - 1, ranges[num_beams - 1]
        );


    }

    // 6.1) Print first LIDAR shape
    // std::printf("ranges[0]:\n");
    // for (int b = 0; b < num_beams; ++b) {
    //     std::printf("  %.3f ", ranges[b]);
    // }
    // std::printf("\n");

    // 7) Inspect first sim
    const T* state0 = sims[0].get_state();
    bool hit0 = sims[0].collided();
    std::printf(
        "Sim[0] -> x=%.3f y=%.3f theta=%.3f collision=%s\n",
        state0[0], state0[1], state0[2],
        hit0 ? "YES" : "no"
    );

    return 0;
}
