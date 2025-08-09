#include <cstdio>
#include <jalansim/map/map_loader.hpp>

using T = float; // Change to double if needed

using jalansim::map::Mode;

int main(int argc, char** argv)
{
    if (argc < 2) {
        printf("Usage: %s <image.[png|jpg|pgm]>\n", argv[0]);
        return 1;
    }
    const char* path = argv[1];

    /* load PNG/JPEG/PGM into a managed map ---------------------------- */
    jalansim::map::Map<T>* map = jalansim::map::load_image<T>(
        path,
        /* resolution  */ 0.05,          // 5 cm / cell
        /* origin_x/y  */ 0.0, 0.0, 0.0,
        /* negate      */ false,
        /* occ_th      */ 0.65,
        /* free_th     */ 0.196,
        /* padding     */ 1,
        /* padding_val */ 0,
        Mode::Trinary);

    printf("CUDA map: %d × %d (scale = %.2f m/cell)  managed = %s\n",
           map->size_x, map->size_y, map->scale, (map->cells_managed) ? "true" : "false");

    /* GPU distance field --------------------------------------------- */
    // map_update_cspace(map, /*max_occ_dist=*/3.0);
    map->update_dist(3.0f);
    
    printf("Occupancy at map origin : %d\n", map->cells[0].occupancy);
    printf("Distance at map origin : %.3f m\n", map->cells[0].dist);

    // map_free(map);
    jalansim::map::Map<T>::destroy(map);
    return 0;
}
