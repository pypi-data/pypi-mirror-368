#include <nanobind/nanobind.h>
#include <jalansim/cuda_macros.hpp>

#include "batch_sim.hpp"
#include "collision/circle.hpp"
#include "collision/polygon.hpp"
#include "dynamics/bicycle.hpp"
#include "dynamics/bicycle_dynamics.hpp"
#include "dynamics/diff_drive.hpp"
#include "map/map.hpp"
#include "map/map_collection.hpp"

namespace nb = nanobind;
using nb::literals::operator""_a;
using T = float;

NB_MODULE(_core_cpu, m)
{
    m.doc() = "Python bindings for jalansim (CPU backend)";
    define_map_class<T>(m);
    define_map_collection_class<T>(m);

    nb::module_ dynamics = m.def_submodule("dynamics", "Dynamics models and utilities");
    define_bicycle_class<T>(dynamics);
    define_diff_drive_class<T>(dynamics);
    define_bicycle_dynamics_class<T>(dynamics);

    nb::module_ collision = m.def_submodule("collision", "Collision models and utilities");
    define_circlecollision_class<T>(collision);
    define_polygoncollision_class<T>(collision);

    using BicycleModel = jalansim::dynamics::models::Bicycle<T>;
    using BicycleDynamicsModel = jalansim::dynamics::models::BicycleDynamics<T>;
    using DiffDriveModel = jalansim::dynamics::models::DiffDrive<T>;
    using CircleCollision = jalansim::collision::CircleCollision<T>;
    using PolygonCollision = jalansim::collision::PolygonCollision<T>;

    define_batchsim_class<T, BicycleModel, CircleCollision>(m, "BicycleCircleBatchSim");
    define_batchsim_class<T, BicycleModel, PolygonCollision>(m, "BicyclePolyBatchSim");

    define_batchsim_class<T, BicycleDynamicsModel, CircleCollision>(m, "BicycleDynCircleBatchSim");
    define_batchsim_class<T, BicycleDynamicsModel, PolygonCollision>(m, "BicycleDynPolyBatchSim");

    define_batchsim_class<T, DiffDriveModel, CircleCollision>(m, "DiffDriveCircleBatchSim");
    define_batchsim_class<T, DiffDriveModel, PolygonCollision>(m, "DiffDrivePolyBatchSim");
}
