# fluidsimfoam-firefoam

FireFoam combustion simulation example for fluidsimfoam.

## Overview

This example demonstrates how to use fluidsimfoam with OpenFOAM's fireFoam solver for combustion simulations. The case includes:

- **Solver**: fireFoam (combustion with spray, surface film and pyrolysis modeling)
- **Mesh**: Complex geometry with snappyHexMesh
- **Physics**: 
  - Multi-species combustion (C7H16, O2, N2)
  - Turbulence modeling (k-epsilon with wall functions)
  - Radiation (P1 model with wide band absorption)
  - Lagrangian spray particles
  - Surface film modeling
  - Pyrolysis zones

## Installation

```bash
pip install -e .
```

## Usage

### Basic Simulation

```python
from fluidsimfoam_firefoam import Simul

params = Simul.create_default_params()

# Configure simulation parameters
params.output.sub_directory = "firefoam_combustion"
params.NEW_DIR_RESULTS = True

# Parallel settings
params.parallel.nsubdoms = 10

# Time settings
params.controlDict.endTime = 150
params.controlDict.deltaT = 0.001
params.controlDict.writeInterval = 1

# Create and run simulation
sim = Simul(params)
sim.make.exec("decomposePar")
sim.make.exec("mpirun", "-np", "10", "fireFoam", "-parallel")
```

### Reading and Plotting Results

The package includes a `CaseLoader` utility for analyzing existing cases:

```python
from pathlib import Path
import sys
sys.path.insert(0, 'doc')
from example_load_case import CaseLoader

# Load an existing case
case_path = Path("path/to/your/case")
case = CaseLoader(case_path, nsubdoms=10)

# Get case information
case.info()
times = case.get_times()

# Read fields
T = case.read_field("T", time_approx="last")
U = case.read_field("U", time_approx="last")
O2 = case.read_field("O2", time_approx="last")

print(f"Temperature range: {T.get_array().min():.2f} to {T.get_array().max():.2f} K")

# For parallel cases, first reconstruct:
case.fields.reconstruct_par(fields=["T", "U", "O2"], latest_time=True)

# Then plot (requires pyvista)
case.fields.plot_contour(variable="T", mesh_opacity=0.1)
case.fields.plot_boundary(name="inlet", color="r")
```

See `doc/example_load_case.py` for a complete working example.

## Case Structure

The template case includes:

- `0/`: Initial and boundary conditions for all fields
- `constant/`: Physical properties, thermophysical models, combustion chemistry
- `system/`: Mesh generation (blockMesh, snappyHexMesh), solver settings, schemes

## Key Features

- **Combustion modeling**: Detailed chemistry with reactions file
- **Radiation**: P1 radiation model with boundary conditions
- **Turbulence**: Standard k-epsilon RANS model
- **Parallel decomposition**: Pre-configured for 10 processors
- **Complex geometry**: Includes STL surfaces and snappyHexMesh configuration

## Dependencies

- fluidsimfoam >= 0.0.7
- OpenFOAM (tested with v2206)
- Python >= 3.9

## References

- [OpenFOAM fireFoam solver](https://www.openfoam.com/documentation/guides/latest/doc/guide-applications-solvers-combustion-fireFoam.html)
- [fluidsimfoam documentation](https://fluidsimfoam.readthedocs.io)

## License

BSD-3-Clause License
