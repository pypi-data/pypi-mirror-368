#pragma once
#include <cstring>
#include <string>
#include <stdexcept>
#include <stb/stb_image.h>
#include "jalansim/map/map.hpp"

namespace jalansim::map
{

    enum class Mode
    {
        Trinary,
        Scale,
        Raw
    };

    template <typename T>
    inline Map<T> *load_image(const std::string &path,
                              T resolution,
                              T origin_x, T origin_y, T yaw,
                              bool negate = false,
                              T occ_th = 0.65,
                              T free_th = 0.196,
                              int padding = 0,
                              int padding_val = 0,
                              Mode mode = Mode::Trinary)
    {
        int w, h, nc;
        unsigned char *data = stbi_load(path.c_str(), &w, &h, &nc, 0);
        if (!data)
        {
            std::string reason = stbi_failure_reason();
            throw std::runtime_error("stb_image failed: " + path + " - " + reason);
        }
        if (!data)
            throw std::runtime_error("stb_image failed: " + path);

        Map<T> *m = Map<T>::create();

        m->resize(w + 2 * padding, h + 2 * padding);
        m->scale = resolution;
        m->origin_x = origin_x;
        m->origin_y = origin_y;

        auto idx = [m](int i, int j)
        { return m->index(i, j); };

        for (int j = 0; j < m->size_y; ++j)
            for (int i = 0; i < m->size_x; ++i)
                m->cells[idx(i, j)].occupancy = int8_t(padding_val);

        for (int j = 0; j < h; ++j)
        {
            for (int i = 0; i < w; ++i)
            {
                unsigned char *px = data + (j * w + i) * nc;

                int ch = (mode == Mode::Raw || nc == 1) ? nc : nc - 1;
                int sum = 0;
                for (int k = 0; k < ch; ++k)
                    sum += px[k];
                double gray = double(sum) / double(ch);
                if (negate)
                    gray = 255.0 - gray;

                int8_t state;
                if (mode == Mode::Raw)
                {
                    state = static_cast<int8_t>(std::lround(gray * 100. / 255.));
                }
                else
                {
                    double occ = (255.0 - gray) / 255.0;
                    if (occ > occ_th)
                        state = +1;
                    else if (occ < free_th)
                        state = -1;
                    else
                        state = (mode == Mode::Trinary) ? 0 : int8_t((occ - free_th) / (occ_th - free_th) * 100);
                }

                m->cells[idx(i + padding, m->size_y - 1 - (j + padding))].occupancy = state;
            }
        }
        stbi_image_free(data);
        return m;
    }

}
