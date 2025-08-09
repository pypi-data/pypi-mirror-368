# JALAN-Sim

A learning-based local navigation simulator for Autonomous Ground Vehicles (AGVs) in complex environments. JALAN-Sim provides efficient Python bindings, customizable build configurations, and support for both CUDA-enabled and CPU-only backends.

## Installation

To get started, clone or download the repository and install in editable mode:

```bash
# Clone the repository
git clone https://github.com/damanikjosh/jalansim.git
cd jalansim

# Install in editable mode
pip install -e .
````

> **Note:** Ensure you have Python ≥ 3.8, CMake ≥ 3.23, and a supported compiler installed.

## Configuring the Build Backend

By default, JALAN-Sim enables CUDA support. If you do *not* have an NVIDIA GPU—or prefer a CPU-only build—edit the `pyproject.toml` file and set the `-DWITH_CUDA` flag to `OFF`:

```toml
[build-system]                  # Tells pip how to build
requires = [
  "scikit-build-core>=0.8",
  "pybind11>=2.13",
  "cmake>=3.23",
  "numpy>=2",
  "ninja"                       # Faster parallel builds
]
build-backend = "scikit_build_core.build"

[project]
name    = "jalansim"
version = "0.1.0"
requires-python = ">=3.8"

[tool.scikit-build]
# Change -DWITH_CUDA to OFF for a CPU-only build
cmake.args = ["-DWITH_PYTHON=ON", "-DWITH_CUDA=OFF"]
```

Save the changes and reinstall:

```bash
pip install -e .
```

## Usage Example

TODO

## License

No license specified yet.
