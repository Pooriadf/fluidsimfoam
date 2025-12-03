# FireFoam Example - Setup Summary

## What Was Created

A complete fluidsimfoam example package for fireFoam combustion simulations has been initialized in:
`doc/examples/fluidsimfoam-firefoam/`

## Directory Structure

```
fluidsimfoam-firefoam/
├── LICENSE                           # BSD-3-Clause license
├── README.md                         # Complete documentation
├── pyproject.toml                    # Package configuration
├── doc/
│   └── example_load_case.py         # Script to load and analyze existing cases
├── src/
│   └── fluidsimfoam_firefoam/
│       ├── __init__.py              # Solver class definition
│       ├── output.py                # Output configuration for fireFoam
│       └── templates/               # Complete OpenFOAM case from F:\...\03dec\2
│           ├── 0/                   # Initial conditions (T, U, p, species, etc.)
│           ├── constant/            # Physical properties, chemistry, radiation
│           ├── system/              # Mesh, solver settings, schemes
│           └── processor0-9/        # Parallel decomposition (10 processors)
└── tests/
    └── test_firefoam.py             # Basic unit tests
```

## Source Case

The OpenFOAM case was copied from:
```
$FOAM_TUTORIALS/combustion/fireFoam/LES/compartmentFire
```

## Case Features

- **Solver**: fireFoam (combustion solver)
- **Physics**:
  - Multi-species combustion (C7H16 fuel, O2, N2)
  - Turbulence modeling (k-epsilon)
  - Radiation (P1 model with boundary conditions)
  - Lagrangian spray particles
  - Surface film modeling
  - Pyrolysis zones

- **Fields**: T, U, p, p_rgh, C7H16, O2, N2, alphat, k, nut, G, IDefault

- **Mesh**: Complex geometry with snappyHexMesh

- **Parallel**: Pre-configured for 10 processors

## Installation

The package has been installed in development mode:
```bash
cd doc/examples/fluidsimfoam-firefoam
pip install -e .
```

Entry point registered: `fluidsimfoam.solvers.firefoam`

## Usage Examples

### 1. Analyze Existing Case

Use the `CaseLoader` utility in `doc/example_load_case.py`:

```python
from pathlib import Path
from example_load_case import CaseLoader

case = CaseLoader("$FOAM_TUTORIALS/combustion/fireFoam/LES/compartmentFire", nsubdoms=10)
case.info()

# Read fields
T = case.read_field("T", time_approx="last")
print(f"Temperature: {T.get_array().min():.2f} - {T.get_array().max():.2f} K")
```

### 2. Create New Simulation

```python
from fluidsimfoam_firefoam import Simul

params = Simul.create_default_params()
params.output.sub_directory = "my_firefoam_case"
params.controlDict.endTime = 150

sim = Simul(params)
sim.make.exec("run")
```

## Key Files Created

1. **`src/fluidsimfoam_firefoam/__init__.py`**: 
   - Defines `InfoSolverFireFoam` and `Simul` classes
   - Registers solver with fluidsimfoam

2. **`src/fluidsimfoam_firefoam/output.py`**:
   - Configures output for fireFoam
   - Lists all field variables and configuration files
   - Sets default controlDict parameters

3. **`doc/example_load_case.py`**:
   - `CaseLoader` class for reading existing cases
   - Example script showing how to read and analyze fields
   - Works with parallel decomposed cases

4. **`tests/test_firefoam.py`**:
   - Unit tests for parameter creation
   - Test case generation
   - Optional simulation test (requires fireFoam)

## Next Steps

1. **To run simulations**: Ensure OpenFOAM is properly sourced in your environment

2. **To analyze results**: Run the example script:
   ```bash
   cd doc/examples/fluidsimfoam-firefoam/doc
   python example_load_case.py
   ```

3. **To plot results**: Install pyvista for 3D visualization:
   ```bash
   pip install pyvista
   ```

4. **To modify the case**: Edit files in `src/fluidsimfoam_firefoam/templates/`

## Testing

Run the tests:
```bash
cd doc/examples/fluidsimfoam-firefoam
pytest tests/
```

## Integration

The package is now available throughout fluidsimfoam:

```python
from fluidsimfoam_firefoam import Simul
# or
from fluidsimfoam.solvers import get_solver
Simul = get_solver("firefoam")
```

## Notes

- The case includes all necessary files for combustion simulation
- Mesh is already created (polyMesh in constant/)
- Case is decomposed for 10 processors
- Chemistry and radiation models are pre-configured
- Initial conditions are set for all species and fields
