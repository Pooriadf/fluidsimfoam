# Quick Start Guide

This guide will get you up and running with Fluidsimfoam in minutes.

## Prerequisites

- Python 3.9 or later
- OpenFOAM v2206 or later (properly sourced in your environment)
- Basic familiarity with OpenFOAM concepts

## Installation

Install Fluidsimfoam from PyPI:

```bash
pip install fluidsimfoam
```

Verify the installation:

```bash
fluidsimfoam-info
```

## Your First Simulation

Let's create and run a simple simulation using the Taylor-Green Vortex (TGV) example.

### Step 1: Create a Simulation Script

Create a file called `my_first_sim.py`:

```python
from fluidsimfoam_tgv import Simul

# Create default parameters
params = Simul.create_default_params()

# Configure the simulation
params.short_name_type_run = "test"
params.NEW_DIR_RESULTS = True

# Set mesh resolution (small for quick testing)
params.block_mesh_dict.nx = 8
params.block_mesh_dict.ny = 8
params.block_mesh_dict.nz = 8

# Set simulation time
params.control_dict.end_time = 1.0
params.control_dict.write_interval = 0.5

# Create and run the simulation
sim = Simul(params)
```

### Step 2: Run the Simulation

```bash
python my_first_sim.py
```

This will:
1. Create a new directory for your simulation
2. Generate all necessary OpenFOAM input files
3. Set up the mesh
4. Initialize the flow field
5. Run the simulation

### Step 3: Load and Analyze Results

After the simulation completes, load it for analysis:

```python
from fluidsimfoam import load

# Load the simulation (specify the path printed during run)
sim = load("path/to/simulation/directory")

# Access simulation data
print(f"Simulation completed: {sim.path_run}")
print(f"Parameters: {sim.params}")

# Read field data (if available)
# fields = sim.output.fields.get_field_files()
```

Or use the convenient IPython loader:

```bash
cd path/to/simulation/directory
fluidsimfoam-ipy-load
```

## Key Concepts

### 1. **Solvers**
A Fluidsimfoam solver is a Python package that defines a set of related simulations. Examples:
- `fluidsimfoam-tgv` - Taylor-Green Vortex
- `fluidsimfoam-phill` - Periodic Hill
- `fluidsimfoam-dam` - Dam Break

### 2. **Parameters**
The `params` object organizes all simulation settings:
```python
params = Simul.create_default_params()
params.control_dict.end_time = 10.0
params.control_dict.delta_t = 0.01
params.fv_solution.solvers.p.tolerance = 1e-7
```

### 3. **Simulation Object**
The `sim` object provides access to:
- `sim.params` - Simulation parameters
- `sim.path_run` - Directory containing simulation files
- `sim.output` - Output management and data access
- `sim.oper` - Mesh operations and utilities
- `sim.make` - Build and execution commands

## Creating Your Own Solver

Generate a solver from an existing OpenFOAM case:

```bash
fluidsimfoam-initiate-solver my_solver -c path/to/openfoam/case
```

This creates a `fluidsimfoam-my_solver` package that you can customize.

## Common Tasks

### Parametric Studies

```python
import numpy as np
from fluidsimfoam_tgv import Simul

# Loop over Reynolds numbers
for re in [100, 500, 1000]:
    params = Simul.create_default_params()
    params.short_name_type_run = f"re{re}"
    params.transport_properties.nu = 1.0 / re
    
    sim = Simul(params)
    # sim.make.exec("run")  # Run in parallel if needed
```

### Custom Initial Conditions

```python
params = Simul.create_default_params()
params.init_fields.type = "from_py"  # Use Python instead of codeStream

sim = Simul(params)

# The _make_tree_u method in your solver's output.py
# can now use NumPy to generate initial conditions
```

### Programmatic Mesh Generation

```python
from fluidsimfoam.foam_input_files.blockmesh import (
    BlockMeshDict, Vertex, HexBlock, SimpleGrading
)

# Create mesh programmatically
bmd = BlockMeshDict()
bmd.set_scale(1.0)

# Add vertices
v0 = bmd.add_vertex(0, 0, 0, "v0")
v1 = bmd.add_vertex(1, 0, 0, "v1")
# ... add more vertices

# Create blocks
block = HexBlock(
    ["v0", "v1", "v2", "v3", "v4", "v5", "v6", "v7"],
    (10, 10, 10),  # cells in x, y, z
    "block0",
    SimpleGrading(1, 1, 1)
)
bmd.add_hexblock(block)

# Set boundaries
bmd.add_boundary("wall", "wall", ["v0", "v1", "v2", "v3"])
```

## Next Steps

- Read the [tutorials](tutorials.md) for detailed examples
- Explore the [API documentation](autosum.rst)
- Check out [example solvers](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples)
- Learn about [best practices](best_practices.md)

## Getting Help

- **Documentation**: https://fluidsimfoam.readthedocs.io
- **Issues**: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/issues
- **Examples**: Check the `doc/examples/` directory in the repository

## Common Issues

**OpenFOAM not found:**
Make sure OpenFOAM is properly sourced in your shell:
```bash
source /path/to/OpenFOAM/etc/bashrc
```

**Import errors:**
Ensure the solver package is installed:
```bash
pip install fluidsimfoam-tgv  # or your solver name
```

**Permission errors:**
Use `--user` flag or a virtual environment:
```bash
pip install --user fluidsimfoam
```
