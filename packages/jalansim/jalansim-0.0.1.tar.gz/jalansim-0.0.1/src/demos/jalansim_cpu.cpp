/*
 * jalansim_single.cpp  –  minimal single-simulator example
 *
 *   • loads an occupancy PGM
 *   • builds one Diff-Drive simulator
 *   • steps the dynamics for 100 iterations
 *   • at every step it:
 *       – queries collision state
 *       – performs a 720-beam 2-D “lidar” scan
 *       – prints a few representative ranges
 *
 *   Compile (CPU only):
 *     g++ -std=c++17 -O3 jalansim_single.cpp -Iinclude -ljalansim -o single_demo
 *
 *   CUDA users can build the same .cpp with nvcc, nothing CUDA-specific
 *   is used here.
 */
#include <cstdio>
#include <vector>
#include <cmath>

#include "jalansim/jalansim.hpp"
#include "jalansim/dynamics/models/diff_drive.hpp"
#include "jalansim/map/map_loader.hpp"
#include "jalansim/collision/collision.hpp"

using T = float;

using DynamicsModel = jalansim::dynamics::models::DiffDrive<T>;
using Collision     = jalansim::collision::CircleCollision<T>;
using Range         = jalansim::range::Bresenham<T>;      // or RayMarching
using Sim           = jalansim::Jalansim<T, DynamicsModel, Collision, Range>;

int main()
{
    /* ───────────────────────── 1. load & preprocess map ───────────────────── */
    jalansim::map::Map<T>* map = jalansim::map::load_image<T>(
        "map_pgm_0.pgm",   /* file                          */
        0.15,              /* resolution   (m / cell)       */
        -2.175, -4.875,    /* origin_x, origin_y            */
        0.0                /* yaw (rad)                     */);
    if (!map) { std::fprintf(stderr, "bad map\n"); return -1; }
    // map_update_cspace(map, 10.0);                        /* chamfer DT */
    map->update_dist(10.0);                        /* chamfer DT */

    /* ───────────────────────── 2. simulator set-up ────────────────────────── */
    DynamicsModel dyn_par;                               /* default model   */
    Collision     col_par;  col_par.radius = 0.75;       /* robot radius    */

    Sim sim(dyn_par, col_par);
    sim.set_map(map);

    /* user control: constant wheel torques */
    const T tau_r = 0.8, tau_l = 0.0;
    const T dt    = 0.1;                            /* time-step (s)   */

    /* lidar parameters */
    const int    beams     = 720;
    const T fov_rad   = 1.5 * M_PI;                 /* 270° */
    const T max_range = 10.0;

    std::vector<T> scan;

    /* ───────────────────────── 3. run the simulation ──────────────────────── */
    sim.reset();
    for (int step = 0; step < 100; ++step)
    {
        /* 3.1 advance dynamics */
        T u[2] = { tau_r, tau_l };
        sim.step(u, dt);

        /* 3.2 collision check */
        bool hit = sim.collided();

        /* 3.3 perform lidar scan (on this single robot) */
        scan = sim.get_range(beams, fov_rad, max_range);

        /* 3.4 sample a few beams for concise output */
        T r0   = scan.front();
        T rMid = scan[beams / 2];
        T rEnd = scan.back();

        std::printf("step %02d | collision=%s | range[0]=%.3f  range[mid]=%.3f  "
                    "range[last]=%.3f\n",
                    step, hit ? "YES" : "no", r0, rMid, rEnd);
    }

    /* ───────────────────────── 4. final state printout ────────────────────── */
    const T* x = sim.get_state();                       /* [x,y,θ] */
    std::printf("final state  x=%.3f  y=%.3f  θ=%.3f\n", x[0], x[1], x[2]);
    return 0;
}
