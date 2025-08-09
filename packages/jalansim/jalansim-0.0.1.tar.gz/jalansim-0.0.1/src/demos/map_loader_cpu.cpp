#include <iostream>
#include "jalansim/map/map_loader.hpp"

using T = double;  // or double, depending on your precision needs

int main(int argc, char** argv)
{
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <image.[png|jpg|pgm]>\n";
        return 1;
    }

    const char* img_path = argv[1];

    /* resolution [m/cell] and origin of the map frame ------------------ */
    double resolution = 0.05;                  // 5 cm per cell
    double origin_x = 0.0;
    double origin_y = 0.0;
    double yaw      = 0.0;                     // no rotation

    /* load the image into a map_t -------------------------------------- */
    jalansim::map::Map<T>* map = jalansim::map::load_image<T>(
        img_path,
        resolution,
        origin_x, origin_y, yaw,
        /* negate      = */ false,             // black = free, white = occ
        /* occ_th      = */ 0.65,              // >65 % → occupied
        /* free_th     = */ 0.196,             // <19.6 % → free
        /* padding     = */ 1,                 // 1-cell unknown border
        /* padding_val = */ 0,                 // unknown state
        jalansim::map::Mode::Trinary);

    std::cout << "CPU map: "
              << map->size_x << " × " << map->size_y
              << " (scale = " << map->scale << " m/cell)  managed = "
              << (map->cells_managed ? "true" : "false") << '\n';

    /* build the distance field (CPU or CUDA, chosen automatically) ----- */
    // map_update_cspace(map, /*max_occ_dist=*/3.0);
    map->update_dist(3.0);  // update distance transform

    std::cout << "Occupancy at map origin : "
              << int(map->cells[0].occupancy) << '\n';

    std::cout << "Distance at map origin : "
              << map->cells[0].dist << " m\n";

    /* always free when done ------------------------------------------- */
    // map_free(map);
    jalansim::map::Map<T>::destroy(map);
    return 0;
}
