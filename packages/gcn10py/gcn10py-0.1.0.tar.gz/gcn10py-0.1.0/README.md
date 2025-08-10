# GCN10Py

**GCN10py** is a Python interface to the high-performance C-based [`gcn10`](https://github.com/mabdazzam/gcn10/tree/main/src/c/mpi)
executable for generating Curve Number (CN) rasters using MPI. It enables
block-based, parallel generation of CN maps from global soil and land cover datasets.

---

## Prerequisites

Ensure the following dependencies are installed and available in your system `PATH`:

- [`gcn10`](https://github.com/mabdazzam/gcn10/tree/main/src/c/mpi) (compiled C executable with MPI and GDAL)
- MPI implementation (e.g., MPICH, OpenMPI)
- GDAL runtime libraries (CLI + C bindings)

---

## Installation

Install via pip:

```bash
pip install gcn10py
```

> **Note**: This package requires a working build of the `gcn10` executable, compiled with MPI and GDAL support.

---

## Building from Source

1. Compile the C binary and place it into:

   ```
   src/gcn10py/gcn10      # or gcn10.exe on Windows
   ```
Follow the instructions [here](https://github.com/mabdazzam/gcn10/tree/main/src/c/)

2. Install the build tools:

   ```bash
   pip install hatchling
   ```

3. Build the wheel package:

   ```bash
   python -m build
   ```

4. Install locally for testing:

   ```bash
   pip install dist/gcn10py-0.1.0-py3-none-any.whl
   ```

---

## Usage

### command-line (required `-c`, optional `-l` and `-o`)

- `-c <path>`: required. path to the `config.txt` used by the C backend.
- `-l <path>`: optional. text file containing block ids (one per line).
- `-o`: optional. overwrite existing outputs.

basic examples:

```bash
# minimal: run using config only
gcn10py -c config.txt

# run and overwrite any existing outputs
gcn10py -c config.txt -o

# run a specific block list
gcn10py -c config.txt -l blocks.txt

# run a specific block list and overwrite outputs
gcn10py -c config.txt -l blocks.txt -o
```

mpi examples:

```bash
# 10 mpi processes, config only
mpirun -n 10 gcn10py -c config.txt

# 10 mpi processes, block list + overwrite
mpirun -n 10 gcn10py -c config.txt -l blocks.txt -o
```

(optional) call the C binary directly:

```bash
mpirun -n 10 ./gcn10 -c config.txt -l blocks.txt -o
```

---

### python api

```python
from gcn10py import run

# run with config only
run(["-c", "config.txt"])

# run with overwrite
run(["-c", "config.txt", "-o"])

# run with a block list
run(["-c", "config.txt", "-l", "blocks.txt"])

# run with a block list and overwrite
run(["-c", "config.txt", "-l", "blocks.txt", "-o"])
```

you can wrap this in your own scripts, add logging, or integrate with job schedulers.

---

### Generate all 18 rasters for an aoi (yaml-driven execution)

a ready-to-use driver and example config live in the **`testing/`** directory:

- `testing/gcn10_driver.py` — orchestrates the full pipeline (discover blocks for your aoi, launch mpi, mosaic, clip)
- `testing/config.yaml` — example configuration (aoi, blocks, mpi settings, mosaic patterns, gdal options)
- test data under `testing/` for quick validation

run it like this:

```bash
# from the project root
cd testing
python gcn10_driver.py -y config.yaml

# or make it executable
chmod a+x gcn10_driver.py
./gcn10_driver.py -y testing/config.yaml
```

what it does:
- reads your aoi (gpkg/shp)
- finds intersecting block ids from `esa_extent_blocks.shp` (or uses a provided list)
- launches `gcn10` via mpi (or uses the python api) to generate per-block cn rasters
- mosaics each of the 18 combinations (hc × arc × drainage) and clips to the aoi
- writes all 18 final geotiffs to the output directory defined in the yaml

notes:
- the driver normalizes paths to absolute and runs with `cwd` set to the directory of `config.txt` so relative paths inside the config resolve consistently
- set `run.cli_cmd: gcn10` or copy the `gcn10` in `testing/config.yaml` if you prefer calling the C binary directly

---

## Project Structure

```text
gcn10py/
├── LICENSE
├── README.md
├── pyproject.toml
├── src/
│   └── gcn10py/
│       ├── __init__.py
│       ├── cli.py
│       └── gcn10         # compiled C executable (excluded from repo)
└── testing/
    └── gcn10_driver.py
    
```

---

## Testing & Benchmarks

### testing
- unit tests (if provided) under `tests/`:
  ```bash
  pytest -q
  ```
- functional check:
  - edit `testing/config.yaml` to point to your AOI and inputs
  - run `testing/gcn10_driver.py -y testing/config.yaml`
  - verify 18 outputs appear in `io.output_dir`

### benchmarks (reference)

measured on:

```
OS: Slackware 15.0+, x86_64
Kernel: 6.12.39
CPU: Intel(R) Core(TM) Ultra 7 165U
CPU(s): 14
Memory: 64 GiB
```

- `gcn10` C binary: 4 blocks, 4 MPI processes → **4 min 15 s**
- `gcn10py` CLI (python wrapper only): same 4 blocks → **5 min 40 s**
- YAML driver (same 4 blocks) + build VRTs + 18 mosaics clipped to AOI → **6 min 34 s**  
  (GDAL threads: `GDAL_NUM_THREADS=ALL_CPUS`, creation options: `TILED=YES, COMPRESS=LZW, BIGTIFF=YES`)

performance will vary with I/O bandwidth, MPI binding, GDAL config, OS and most importantly internet connection.
For best performance, use linux native utilities.

---

## License

Copyright (C) 2025  
**Abdullah Azzam** ([mabdazzam](https://github.com/mabdazzam))

Released under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html).  
See the `LICENSE` file for full terms.

---

## Contact

Questions, bug reports, or contributions? Open an issue or pull request on [GitHub](https://github.com/mabdazzam/gcn10py).
