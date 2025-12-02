# Introduction

## Overview

```{include} ../README.md
---
start-after: <!-- start-intro -->
end-before: <!-- end-intro -->
---
```

## Core Features

### 1. Python-Based Workflow

Replace manual file editing with Python code:

**Traditional OpenFOAM:**
```bash
# Copy a tutorial
cp -r $FOAM_TUTORIALS/incompressible/icoFoam/cavity myCase
cd myCase

# Edit files manually
vi system/controlDict  # Change endTime, deltaT, etc.
vi system/blockMeshDict  # Modify mesh parameters
vi 0/U  # Set boundary conditions
vi 0/p  # Set initial pressure

# Run commands
blockMesh
icoFoam
```

**With Fluidsimfoam:**
```python
from fluidsimfoam_cavity import Simul

# Set parameters in Python
params = Simul.create_default_params()
params.control_dict.end_time = 5.0
params.control_dict.delta_t = 0.005
params.block_mesh_dict.nx = 40
params.block_mesh_dict.ny = 40

# Create and run
sim = Simul(params)
```

### 2. Programmatic File Generation

Generate complex input files using Python APIs:

```python
from fluidsimfoam.foam_input_files.blockmesh import BlockMeshDict

# Create mesh programmatically
bmd = BlockMeshDict()
for i, x in enumerate(np.linspace(0, 1, nx+1)):
    for j, y in enumerate(np.linspace(0, 1, ny+1)):
        bmd.add_vertex(x, y, 0, f"v{i}_{j}")

# Add parametric grading, boundaries, etc.
```

### 3. Reproducible Simulations

All parameters are stored in XML format:

```xml
<!-- params_simul.xml -->
<params>
  <control_dict>
    <end_time>5.0</end_time>
    <delta_t>0.005</delta_t>
  </control_dict>
  <transport_properties>
    <nu>0.001</nu>
  </transport_properties>
</params>
```

This ensures:
- Complete parameter history
- Easy reproduction of results
- Version control friendly
- Comparison between cases

### 4. Parametric Studies Made Easy

Run parameter sweeps with simple loops:

```python
for reynolds in [100, 500, 1000, 5000]:
    params = Simul.create_default_params()
    params.short_name_type_run = f"re{reynolds:05d}"
    params.transport_properties.nu = 1.0 / reynolds
    sim = Simul(params)
```

### 5. Integration with Python Ecosystem

Leverage powerful Python libraries:

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Use NumPy for field initialization
x, y, z = sim.oper.get_cells_coords()
velocity = np.sin(np.pi * x) * np.cos(np.pi * y)

# Matplotlib for visualization
plt.contourf(x, y, velocity)

# SciPy for optimization
result = minimize(objective_function, initial_guess)
```

## When to Use Fluidsimfoam

### ✅ Ideal For

- **Parametric studies** - Running many similar simulations with varying parameters
- **Optimization workflows** - Coupling simulations with optimization algorithms
- **Complex mesh generation** - Programmatically creating parametrized geometries
- **Automation** - Setting up CI/CD pipelines for simulations
- **Reproducibility** - Ensuring simulations can be exactly reproduced
- **Python users** - Leveraging Python skills for CFD

### ⚠️ May Not Be Ideal For

- **One-off simulations** - If you're only running once, standard OpenFOAM might be simpler
- **Existing workflows** - If you have extensive shell scripts that work well
- **GUI preference** - If you prefer graphical tools over code
- **Very custom solvers** - Highly specialized simulations might need manual setup

## Comparison with Other Tools

| Aspect | Fluidsimfoam | Pure OpenFOAM | PyFoam |
|--------|-------------|--------------|---------|
| **Workflow** | Python-first | Shell scripts | Python utilities |
| **File generation** | Programmatic | Manual editing | Manipulation |
| **Parameters** | Hierarchical object | Text files | Dictionaries |
| **Parametric studies** | Built-in | Manual scripting | Case manipulation |
| **Learning curve** | Python + OpenFOAM | OpenFOAM | Python + OpenFOAM |
| **Flexibility** | High | Highest | Medium |

## Architecture at a Glance

```
┌─────────────────────────────────────────┐
│         Your Python Script              │
│  params = Simul.create_default_params() │
│  sim = Simul(params)                    │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Fluidsimfoam Framework          │
│  • Parameter management                 │
│  • File generation                      │
│  • Workflow automation                  │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        OpenFOAM Input Files             │
│  system/, constant/, 0/                 │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│           OpenFOAM Solvers              │
│  blockMesh, icoFoam, simpleFoam, etc.   │
└─────────────────────────────────────────┘
```

## Example: Taylor-Green Vortex

Here's a complete example of setting up and running a simulation:

```python
from fluidsimfoam_tgv import Simul
from fluidsimfoam import load

# 1. Create parameters
params = Simul.create_default_params()

# 2. Configure simulation
params.short_name_type_run = "demo"
params.control_dict.end_time = 10.0
params.control_dict.write_interval = 1.0

# 3. Set mesh resolution
params.block_mesh_dict.nx = 32
params.block_mesh_dict.ny = 32
params.block_mesh_dict.nz = 32

# 4. Physical properties
params.transport_properties.nu = 0.001  # Kinematic viscosity

# 5. Create simulation
sim = Simul(params)
print(f"Simulation created: {sim.path_run}")

# 6. Run simulation (optional, can be done separately)
# sim.make.exec("run")

# 7. Later: load and analyze
sim = load(sim.path_run)
# Access results, generate plots, etc.
```

## Key Concepts

### Solvers

A **Fluidsimfoam solver** is a Python package that describes a family of related simulations. Each solver:

- Defines default parameters
- Specifies how to generate OpenFOAM input files
- Can include custom post-processing

Examples: `fluidsimfoam-tgv`, `fluidsimfoam-phill`, `fluidsimfoam-dam`

### Parameters

The **params** object is a hierarchical container for all simulation settings:

```python
params.control_dict.end_time          # Time integration
params.fv_solution.solvers.p.solver   # Numerical methods
params.transport_properties.nu        # Physical properties
params.block_mesh_dict.nx             # Mesh resolution
```

### Simulation Object

The **sim** object provides access to:

```python
sim.params          # Parameters used
sim.path_run        # Directory location
sim.output          # Output management
sim.oper            # Mesh operations
sim.make            # Build commands
```

## Next Steps

Ready to get started?

1. **[Install Fluidsimfoam](install.md)** - Set up your environment
2. **[Quick Start Guide](quickstart.md)** - Create your first simulation
3. **[Tutorials](tutorials.md)** - Learn through detailed examples
4. **[Best Practices](best_practices.md)** - Write better simulation code

Have questions? Check the **[FAQ](faq.md)** or explore the **[Architecture](architecture.md)** for deeper understanding.
