#include <cstdio>
#include <cmath>
#include "jalansim/cuda_macros.hpp"

#include "jalansim/jalansim.hpp"
#include "jalansim/dynamics/models/diff_drive.hpp"
#include "jalansim/map/map_loader.hpp"
#include "jalansim/collision/collision.hpp"
#include "jalansim/batch/batch.hpp"

using T = float;

using DynamicsModel  = jalansim::dynamics::models::DiffDrive<T>;
using Collision      = jalansim::collision::CircleCollision<T>;
using Range         = jalansim::range::Bresenham<T>;
using Sim           = jalansim::Jalansim<T, DynamicsModel, Collision, Range>;

int main() {
    // 1) Load occupancy map
    auto* map = jalansim::map::load_image<T>("../map_files/map_pgm_0.pgm", 0.15, -2.175, -4.875, 0.0);
    if (!map) {
        std::fprintf(stderr, "Failed to load map\n");
        return -1;
    }
    // map_update_cspace(map, 10.0); // update c-space
    map->update_dist(T(10.0)); // update c-space

    // 2) Configure dynamics and collision parameters
    DynamicsModel dyn_params;
    Collision     collision_params;
    collision_params.radius = 0.75;

    // 3) Allocate managed memory for sims and inputs
    constexpr std::size_t N = 10000000;
    Sim*    sims;
    T* inputs;
    cudaMallocManaged(&sims,   sizeof(Sim)    * N);
    cudaMallocManaged(&inputs, sizeof(T)  * N * DynamicsModel::INPUT_DIM);

    // 4) Construct each simulator and init inputs
    for (std::size_t i = 0; i < N; ++i) {
    //     new(&sims[i]) Sim(dyn_params, collision_params); // placement-new
    //     sims[i].set_map(map);
        inputs[i * DynamicsModel::INPUT_DIM]     = 1.0;  // previously tau_r
        inputs[i * DynamicsModel::INPUT_DIM + 1] = 0.0;  // previously tau_l
    }

    jalansim::batch::init<Sim>(
        sims,
        dyn_params,
        collision_params,
        N
    );
    jalansim::batch::set_map<T, Sim>(
        sims,
        map,
        N
    );
    cudaDeviceSynchronize();

    // 5) Prepare LIDAR parameters & buffer (managed)
    const int    num_beams = 720;
    const T fov       = 1.5 * M_PI;   // full 360°
    const T max_range = 10.0;         // meters
    T* ranges;
    cudaMallocManaged(&ranges,
                      sizeof(T) * N * std::size_t(num_beams));
    bool* hits;
    cudaMallocManaged(&hits,
                      sizeof(bool) * N);

    // 6) Run batch operations + LIDAR on GPU
    jalansim::batch::reset<T, Sim>(sims, N);
    cudaDeviceSynchronize();

    for (int step = 0; step < 100; ++step) {
        // dynamics update
        jalansim::batch::step<T, Sim>(
            sims,
            inputs,
            0.1,  // dt
            N
        );
        cudaDeviceSynchronize();

        // LIDAR scan over all sims × beams
        jalansim::batch::get_range<T, Sim>(
            sims,
            ranges,
            num_beams,
            fov,
            max_range,
            N
        );

        // check collisions
        jalansim::batch::collided<Sim>(
            sims,
            hits,
            N
        );
        cudaDeviceSynchronize();

        // print the shape (N, num_beams)
        std::printf(
            "Step %d — hit[0] = %s, "
            "ranges[0][0] = %.3f, ranges[0][%d] = %.3f, ranges[0][%d] = %.3f\n",
            step,
            hits[0] ? "YES" : "no",
            ranges[0],
            num_beams / 2, ranges[num_beams / 2],
            num_beams - 1, ranges[num_beams - 1]
        );
    }
    cudaDeviceSynchronize();

    // 7) Inspect and print first simulator
    const T* state0 = sims[0].get_state();
    bool hit0 = sims[0].collided();
    std::printf(
        "GPU Sim[0] -> x=%.3f y=%.3f theta=%.3f collision=%s\n",
        state0[0], state0[1], state0[2],
        hit0 ? "YES" : "no"
    );

    // 8) Clean up
    for (std::size_t i = 0; i < N; ++i) sims[i].~Sim();
    cudaFree(ranges);
    cudaFree(sims);
    cudaFree(inputs);
    cudaFree(hits);

    // map_free(map);
    jalansim::map::Map<T>::destroy(map);

    return 0;
}
