#pragma once

#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <algorithm>
#include <queue>
#include <limits>
#include <new>
#include "jalansim/cuda_macros.hpp"

namespace jalansim::map
{

    template <typename T>
    struct Map;

    template <typename T>
    struct MapCell
    {
        int8_t occupancy;
        T dist;
    };

#if JALANSIM_CUDA_ENABLED

    template <typename T>
    __global__ static void
    jacobi_kernel(MapCell<T> *cells, int w, int h, T scale)
    {
        int idx = blockIdx.x * blockDim.x + threadIdx.x;
        const int N = w * h;
        if (idx >= N)
            return;
        if (cells[idx].dist == T(0.0))
            return;

        int i = idx % w, j = idx / w;
        const int off[8][3] = {
            {-1, 0, 1}, {1, 0, 1}, {0, -1, 1}, {0, 1, 1}, {-1, -1, 2}, {1, -1, 2}, {-1, 1, 2}, {1, 1, 2}};
        const T sqrt2 = T(1.414213562373095);
        T best = cells[idx].dist;
        for (int k = 0; k < 8; ++k)
        {
            int ni = i + off[k][0], nj = j + off[k][1];
            if (ni < 0 || nj < 0 || ni >= w || nj >= h)
                continue;
            T step = (off[k][2] == 1) ? scale : scale * sqrt2;
            T nval = cells[ni + nj * w].dist + step;
            best = fmin(best, nval);
        }
        cells[idx].dist = best;
    }

    template <typename T>
    __global__ void jf_kernel(MapCell<T> *cells,
                              int w, int h,
                              T scale,
                              int stride)
    {
        int idx = blockIdx.x * blockDim.x + threadIdx.x;
        int N = w * h;
        if (idx >= N)
            return;

        int x = idx % w;
        int y = idx / w;

        const int dx[8] = {-1, 1, 0, 0, -1, -1, 1, 1};
        const int dy[8] = {0, 0, -1, 1, -1, 1, -1, 1};
        const T diag = scale * T(1.414213562373095);

        T best = cells[idx].dist;

        for (int k = 0; k < 8; ++k)
        {
            int nx = x + dx[k] * stride;
            int ny = y + dy[k] * stride;
            if (nx < 0 || ny < 0 || nx >= w || ny >= h)
                continue;

            int nidx = nx + ny * w;
            T step = (dx[k] == 0 || dy[k] == 0) ? scale * stride : diag * stride;
            T cand = cells[nidx].dist + step;
            best = fmin(best, cand);
        }
        cells[idx].dist = best;
    }

    template <typename T>
    __global__ void dt_pass_vertical(MapCell<T> *c, int w, int h, T scale)
    {
        int x = blockIdx.x * blockDim.x + threadIdx.x;
        if (x >= w)
            return;
        for (int y = 1; y < h; ++y)
        {
            int idx = x + y * w;
            c[idx].dist = fmin(c[idx].dist, c[idx - w].dist + scale);
        }
        for (int y = h - 2; y >= 0; --y)
        {
            int idx = x + y * w;
            c[idx].dist = fmin(c[idx].dist, c[idx + w].dist + scale);
        }
    }

    template <typename T>
    __global__ void dt_pass_horizontal(MapCell<T> *c, int w, int h, T scale)
    {
        int y = blockIdx.x * blockDim.x + threadIdx.x;
        if (y >= h)
            return;
        int base = y * w;
        for (int x = 1; x < w; ++x)
        {
            int idx = base + x;
            c[idx].dist = fmin(c[idx].dist, c[idx - 1].dist + scale);
        }
        for (int x = w - 2; x >= 0; --x)
        {
            int idx = base + x;
            c[idx].dist = fmin(c[idx].dist, c[idx + 1].dist + scale);
        }
    }

    template <typename T>
    __global__ void dt_pass_diagonal(MapCell<T> *c, int w, int h, T diag_step)
    {
        int idx = blockIdx.x * blockDim.x + threadIdx.x;
        if (idx >= w * h || c[idx].dist == T(0.0))
            return;
        int x = idx % w, y = idx / w;
        const int dx[4] = {-1, 1, -1, 1}, dy[4] = {-1, -1, 1, 1};
        T best = c[idx].dist;
        for (int k = 0; k < 4; ++k)
        {
            int nx = x + dx[k], ny = y + dy[k];
            if (nx >= 0 && ny >= 0 && nx < w && ny < h)
            {
                best = fmin(best, c[nx + ny * w].dist + diag_step);
            }
        }
        c[idx].dist = best;
    }

#endif

    template <typename T>
    struct Map
    {
    public:
        T origin_x, origin_y;
        T scale;
        int size_x, size_y;
        MapCell<T> *cells;
        T max_dist;
        uint8_t cells_managed;

        static Map<T> *create()
        {
#if JALANSIM_CUDA_ENABLED
            void *p;
            cudaMallocManaged(&p, sizeof(Map<T>));
            return new (p) Map<T>();
#else
            return new Map<T>();
#endif
        }

        static void destroy(Map<T> *m)
        {
            if (!m)
                return;
#if JALANSIM_CUDA_ENABLED
            m->~Map();
            cudaFree(m);
#else
            delete m;
#endif
        }

        void resize(int sx, int sy)
        {
            size_t n = static_cast<size_t>(sx) * sy;
            if (this->cells)
            {
#if JALANSIM_CUDA_ENABLED
                if (this->cells_managed)
                    cudaFree(this->cells);
                else
                    std::free(this->cells);
#else
                std::free(this->cells);
#endif
            }
#if JALANSIM_CUDA_ENABLED
            cudaMallocManaged(&this->cells, n * sizeof(MapCell<T>));
            this->cells_managed = 1;
#else
            this->cells = (MapCell<T> *)std::malloc(n * sizeof(MapCell<T>));
            this->cells_managed = 0;
#endif
            this->size_x = sx;
            this->size_y = sy;
        }

        Map<T> *clone() const
        {
            Map<T> *dst = Map<T>::create();
            dst->origin_x = this->origin_x;
            dst->origin_y = this->origin_y;
            dst->scale = this->scale;
            dst->max_dist = this->max_dist;
            dst->cells_managed = this->cells_managed;

            dst->resize(this->size_x, this->size_y);

            size_t bytes = static_cast<size_t>(this->size_x) * this->size_y * sizeof(MapCell<T>);
            if (bytes > 0)
            {
#if JALANSIM_CUDA_ENABLED
                cudaMemcpy(dst->cells, this->cells, bytes, cudaMemcpyDefault);
#else
                std::memcpy(dst->cells, this->cells, bytes);
#endif
            }
            return dst;
        }

        void update_dist(T max_d)
        {
#if JALANSIM_CUDA_ENABLED
            update_dist_cuda(max_d);
#else
            update_dist_cpu(max_d);
#endif
        }

        JALANSIM_HOST_DEVICE
        T interpolate_dist(T i, T j) const
        {
            int i0 = int(std::floor(i));
            int j0 = int(std::floor(j));
            if (!is_valid(i0, j0))
                return this->max_dist;

            int i1 = (i0 + 1 < this->size_x) ? i0 + 1 : i0;
            int j1 = (j0 + 1 < this->size_y) ? j0 + 1 : j0;

            T fi = i - i0;
            T fj = j - j0;

            T d00 = this->cells[index(i0, j0)].dist;
            T d10 = this->cells[index(i1, j0)].dist;
            T d01 = this->cells[index(i0, j1)].dist;
            T d11 = this->cells[index(i1, j1)].dist;

            T dx0 = d00 * (T(1.0) - fi) + d10 * fi;
            T dx1 = d01 * (T(1.0) - fi) + d11 * fi;

            return dx0 * (T(1.0) - fj) + dx1 * fj;
        }

        JALANSIM_HOST_DEVICE size_t index(int i, int j) const { return (size_t)i + (size_t)j * size_x; }
        JALANSIM_HOST_DEVICE bool is_valid(int i, int j) const { return (i >= 0 && i < size_x) && (j >= 0 && j < size_y); }

        JALANSIM_HOST_DEVICE T to_x(int i) const { return origin_x + i * scale; }
        JALANSIM_HOST_DEVICE T to_y(int j) const { return origin_y + j * scale; }

        JALANSIM_HOST_DEVICE int to_i(T x) const { return std::round((x - origin_x) / scale); }
        JALANSIM_HOST_DEVICE int to_j(T y) const { return std::round((y - origin_y) / scale); }

        JALANSIM_HOST_DEVICE T to_if(T x) const { return (x - origin_x) / scale; }
        JALANSIM_HOST_DEVICE T to_jf(T y) const { return (y - origin_y) / scale; }

    private:
        Map()
            : origin_x(T(0)), origin_y(T(0)), scale(T(0)),
              size_x(0), size_y(0), cells(nullptr),
              max_dist(T(0)), cells_managed(0)
        {
#if JALANSIM_CUDA_ENABLED
            cudaMallocManaged(&this->cells, sizeof(MapCell<T>));
            this->cells_managed = 1;
#else
            this->cells = (MapCell<T> *)std::malloc(sizeof(MapCell<T>));
#endif
        }

        ~Map()
        {
            if (!cells)
                return;
#if JALANSIM_CUDA_ENABLED
            if (cells_managed)
                cudaFree(cells);
            else
                std::free(cells);
#else
            std::free(cells);
#endif
        }

        Map(const Map<T> &) = delete;
        Map<T> &operator=(const Map<T> &) = delete;

        void update_dist_cpu(T max_d)
        {
            this->max_dist = max_d;
            const int w = this->size_x;
            const int h = this->size_y;
            const int N = w * h;

            for (int idx = 0; idx < N; ++idx)
            {
                this->cells[idx].dist = (this->cells[idx].occupancy > -1) ? T(0.0) : max_d;
            }

            const T sqrt2_scale = T(M_SQRT2) * this->scale;

            for (int j = 0; j < h; ++j)
            {
                for (int i = 0; i < w; ++i)
                {
                    T d = this->cells[index(i, j)].dist;
                    if (d == T(0.0))
                        continue;
                    T best = d;
                    if (i > 0)
                        best = std::min(best, this->cells[index(i - 1, j)].dist + this->scale);
                    if (j > 0)
                        best = std::min(best, this->cells[index(i, j - 1)].dist + this->scale);
                    if (i > 0 && j > 0)
                        best = std::min(best, this->cells[index(i - 1, j - 1)].dist + sqrt2_scale);
                    this->cells[index(i, j)].dist = best;
                }
            }

            for (int j = h - 1; j >= 0; --j)
            {
                for (int i = w - 1; i >= 0; --i)
                {
                    T d = this->cells[index(i, j)].dist;
                    T best = d;
                    if (i < w - 1)
                        best = std::min(best, this->cells[index(i + 1, j)].dist + this->scale);
                    if (j < h - 1)
                        best = std::min(best, this->cells[index(i, j + 1)].dist + this->scale);
                    if (i < w - 1 && j < h - 1)
                        best = std::min(best, this->cells[index(i + 1, j + 1)].dist + sqrt2_scale);
                    this->cells[index(i, j)].dist = best;
                }
            }
        }

#if JALANSIM_CUDA_ENABLED
        void update_dist_cuda(T max_d)
        {
            this->max_dist = max_d;
            const int N = this->size_x * this->size_y;
            const int w = this->size_x;
            const int h = this->size_y;

            for (int idx = 0; idx < N; ++idx)
            {
                this->cells[idx].dist = (this->cells[idx].occupancy > -1) ? T(0.0) : max_d;
            }

            int threads = 256, blocks = (N + threads - 1) / threads;
            int iters = this->size_x + this->size_y;
            for (int k = 0; k < iters; ++k)
            {
                jacobi_kernel<T><<<blocks, threads>>>(this->cells, w, h, this->scale);
            }
            check_cuda();
        }
#endif
    };

}