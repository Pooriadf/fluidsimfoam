# Best Practices

Guidelines for effective use of Fluidsimfoam in your CFD workflows.

## Project Organization

### Directory Structure

Organize your Fluidsimfoam projects with clear structure:

```
my_cfd_project/
├── solvers/                    # Custom solver packages
│   └── fluidsimfoam-mycase/
├── scripts/                    # Simulation launch scripts
│   ├── parametric_study.py
│   ├── single_run.py
│   └── post_process.py
├── results/                    # Simulation outputs (gitignored)
├── notebooks/                  # Analysis notebooks
│   └── analyze_results.ipynb
├── docs/                       # Project documentation
├── tests/                      # Test scripts
├── requirements.txt            # Python dependencies
└── README.md
```

### Version Control

**Do commit**:
- Python scripts and solver code
- Parameter templates
- Test cases
- Documentation

**Don't commit**:
- Simulation result directories
- Large field files
- Compiled files (`*.pyc`, `__pycache__`)
- PDM/poetry lock files (usually)

**Example `.gitignore`**:
```gitignore
# Simulation results
results/
*.foam
processor*/
postProcessing/

# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
.pytest_cache/

# PDM
__pypackages__/
.pdm.toml

# IDEs
.vscode/
.idea/
```

## Parameter Management

### Use Hierarchical Parameters

Organize parameters logically:

```python
# Good: Clear hierarchy
params.control_dict.end_time = 100.0
params.fv_solution.solvers.p.tolerance = 1e-7
params.block_mesh_dict.nx = 64

# Avoid: Flat structure
params.end_time = 100.0  # Ambiguous
```

### Create Parameter Factories

For common configurations:

```python
def create_turbulent_params(re_number, mesh_size="coarse"):
    """Factory for turbulent flow parameters."""
    params = Simul.create_default_params()
    
    params.turbulence_properties.simulation_type = "RAS"
    params.turbulence_properties.RAS.model = "kOmegaSST"
    
    params.transport_properties.nu = 1.0 / re_number
    
    mesh_sizes = {
        "coarse": (32, 32, 32),
        "medium": (64, 64, 64),
        "fine": (128, 128, 128)
    }
    nx, ny, nz = mesh_sizes[mesh_size]
    params.block_mesh_dict.nx = nx
    params.block_mesh_dict.ny = ny
    params.block_mesh_dict.nz = nz
    
    return params
```

### Document Your Parameters

Add docstrings to parameter completion methods:

```python
@classmethod
def _complete_params_with_default(cls, params):
    """Complete simulation parameters.
    
    Parameters added:
    - my_custom_param (float): Controls X behavior, default 1.0
    - my_option (str): Choose from 'A', 'B', 'C', default 'A'
    """
    params._set_attrib("my_custom_param", 1.0)
    params._set_attrib("my_option", "A")
```

## Solver Development

### Start from Examples

Base new solvers on existing ones:

```bash
# Generate from OpenFOAM tutorial
fluidsimfoam-initiate-solver mysolver -c $FOAM_TUTORIALS/path/to/case

# Or copy and modify an example
cp -r doc/examples/fluidsimfoam-tgv my-project/fluidsimfoam-mysolver
```

### Follow Naming Conventions

```python
# Solver package
fluidsimfoam-descriptive_name

# Module structure
fluidsimfoam_descriptive_name/
├── __init__.py       # Contains Simul and InfoSolver
├── output.py         # Contains OutputCustom
└── operators.py      # (optional) Custom OperatorsCustom
```

### Use Type Hints

Make your code more maintainable:

```python
from pathlib import Path
from typing import Optional
from fluidsimfoam.params import Parameters

def process_simulation(
    path_run: Path,
    output_format: str = "vtk",
    verbose: bool = True
) -> Optional[dict]:
    """Process simulation results."""
    ...
```

### Test Your Solver

Create basic tests:

```python
# tests/test_mysolver.py
from fluidsimfoam_mysolver import Simul

def test_create_params():
    """Test parameter creation."""
    params = Simul.create_default_params()
    assert params.control_dict.end_time > 0

def test_simulation_setup():
    """Test simulation initialization."""
    params = Simul.create_default_params()
    params.NEW_DIR_RESULTS = False
    params.output.HAS_TO_SAVE = False
    
    sim = Simul(params)
    assert sim.path_run is not None
```

## Mesh Generation

### Prefer Programmatic BlockMesh

Instead of hand-editing `blockMeshDict`:

```python
from fluidsimfoam.foam_input_files.blockmesh import (
    BlockMeshDict, SimpleGrading
)

def create_channel_mesh(length, height, nx, ny):
    """Create parametric channel mesh."""
    bmd = BlockMeshDict()
    
    # Vertices
    v0 = bmd.add_vertex(0, 0, 0, "v0")
    v1 = bmd.add_vertex(length, 0, 0, "v1")
    v2 = bmd.add_vertex(length, height, 0, "v2")
    v3 = bmd.add_vertex(0, height, 0, "v3")
    # ... add z-direction vertices
    
    # Block with grading
    block = bmd.add_hexblock(
        ["v0", "v1", "v2", "v3", "v4", "v5", "v6", "v7"],
        (nx, ny, 1),
        "main",
        SimpleGrading(1, 1, 1)
    )
    
    # Boundaries
    bmd.add_boundary("inlet", "patch", [["v0", "v3", "v7", "v4"]])
    bmd.add_boundary("outlet", "patch", [["v1", "v2", "v6", "v5"]])
    bmd.add_boundary("walls", "wall", [
        ["v0", "v1", "v5", "v4"],
        ["v3", "v2", "v6", "v7"]
    ])
    
    return bmd
```

### Use Mesh Refinement Parameters

Make mesh resolution a parameter:

```python
params._set_child(
    "mesh",
    attribs={
        "base_resolution": 32,
        "refinement_level": 0,  # 0, 1, 2 for coarse/medium/fine
    }
)

# In mesh generation
nx = params.mesh.base_resolution * (2 ** params.mesh.refinement_level)
```

## Initial Conditions

### Python vs CodeStream

**Use Python** (recommended) when:
- Field initialization requires complex logic
- Using NumPy/SciPy for analytical solutions
- Debugging field generation
- Fields depend on parameters

```python
def _make_tree_u(self, params):
    field = VolVectorField("U", "m/s")
    
    if params.init_fields.type == "from_py":
        x, y, z = self.sim.oper.get_cells_coords()
        # NumPy expressions
        vx = params.u_inf * np.sin(x) * np.cos(y)
        vy = -params.u_inf * np.cos(x) * np.sin(y)
        vz = np.zeros_like(x)
        field.set_values(vx, vy, vz)
    
    return field
```

**Use CodeStream** when:
- Performance is critical (large meshes)
- Using OpenFOAM's built-in functions
- Integration with existing OpenFOAM code

## Parametric Studies

### Use Descriptive Run Names

```python
def run_reynolds_study():
    """Run parametric study over Reynolds numbers."""
    for re in [100, 500, 1000, 5000]:
        params = Simul.create_default_params()
        
        # Descriptive naming
        params.short_name_type_run = f"re{re:05d}"
        params.transport_properties.nu = params.u_ref * params.l_ref / re
        
        sim = Simul(params)
```

### Automate Post-Processing

Create analysis pipelines:

```python
from pathlib import Path
import pandas as pd
from fluidsimfoam import load

def analyze_study(study_dir: Path) -> pd.DataFrame:
    """Analyze all simulations in a study."""
    results = []
    
    for sim_dir in study_dir.glob("*"):
        if not sim_dir.is_dir():
            continue
        
        try:
            sim = load(sim_dir)
            
            # Extract metrics
            result = {
                "case": sim_dir.name,
                "re": extract_reynolds(sim.params),
                "drag": compute_drag(sim),
                "lift": compute_lift(sim),
            }
            results.append(result)
        except Exception as e:
            print(f"Failed to process {sim_dir}: {e}")
    
    return pd.DataFrame(results)
```

### Use Configuration Files

For large studies:

```yaml
# study_config.yaml
study_name: reynolds_sweep
base_params:
  end_time: 100.0
  write_interval: 10.0

variations:
  - re: [100, 200, 500, 1000]
  - mesh_size: ["coarse", "medium", "fine"]
```

```python
import yaml

def run_from_config(config_file):
    with open(config_file) as f:
        config = yaml.safe_load(f)
    
    for re in config["variations"][0]["re"]:
        for mesh in config["variations"][1]["mesh_size"]:
            params = create_params(re, mesh, config["base_params"])
            sim = Simul(params)
```

## Performance

### Parallelize Wisely

```python
# Set up parallel decomposition
params.decompose_par_dict.n_subdomains = 4
params.decompose_par_dict.method = "scotch"

# For large cases
if params.block_mesh_dict.nx > 64:
    params.decompose_par_dict.n_subdomains = 8
```

### Monitor Memory Usage

```python
import psutil

def check_resources():
    """Check available system resources."""
    mem = psutil.virtual_memory()
    print(f"Available memory: {mem.available / 1e9:.1f} GB")
    print(f"CPU count: {psutil.cpu_count()}")
    
    # Adjust simulation accordingly
    if mem.available < 8e9:  # Less than 8 GB
        print("Warning: Limited memory. Use smaller mesh.")
```

### Profile Your Code

```python
import cProfile
import pstats

def profile_simulation():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run simulation
    params = Simul.create_default_params()
    sim = Simul(params)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
```

## Error Handling

### Validate Parameters

```python
@classmethod
def _complete_params_with_default(cls, params):
    params._set_attrib("reynolds", 1000.0)
    
def __init__(self, params):
    # Validate before starting
    if params.reynolds <= 0:
        raise ValueError(f"Reynolds number must be positive, got {params.reynolds}")
    
    if params.control_dict.delta_t <= 0:
        raise ValueError("Time step must be positive")
    
    super().__init__(params)
```

### Graceful Cleanup

```python
import signal
from contextlib import contextmanager

@contextmanager
def simulation_context(sim):
    """Context manager for safe simulation execution."""
    def signal_handler(sig, frame):
        print("\nCaught interrupt, stopping simulation...")
        sim.stop_time_loop()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        yield sim
    finally:
        # Cleanup
        print("Simulation context closed")

# Usage
with simulation_context(sim) as s:
    s.make.exec("run")
```

## Documentation

### Document Your Solver

Create comprehensive README:

```markdown
# Fluidsimfoam-MySolver

## Description
Brief description of the flow problem and solver capabilities.

## Installation
\`\`\`bash
pip install fluidsimfoam-mysolver
\`\`\`

## Quick Start
\`\`\`python
from fluidsimfoam_mysolver import Simul
...
\`\`\`

## Parameters
Document key parameters and their effects.

## Examples
Link to example scripts and notebooks.

## References
Cite relevant papers and documentation.
```

### Add Docstrings

```python
def _make_tree_blockMeshDict(self, params):
    """Generate blockMeshDict for channel geometry.
    
    Creates a structured hexahedral mesh for a 3D channel.
    Supports parametric geometry via params.geometry.
    
    Parameters
    ----------
    params : Parameters
        Simulation parameters containing geometry specifications:
        - params.geometry.length: Channel length [m]
        - params.geometry.height: Channel height [m]
        - params.geometry.width: Channel width [m]
        - params.mesh.nx: Cells in x-direction
        - params.mesh.ny: Cells in y-direction
        - params.mesh.nz: Cells in z-direction
    
    Returns
    -------
    BlockMeshDict
        Configured mesh dictionary
    
    Examples
    --------
    >>> params = Simul.create_default_params()
    >>> params.geometry.length = 10.0
    >>> params.mesh.nx = 100
    >>> output = Output(sim)
    >>> bmd = output._make_tree_blockMeshDict(params)
    """
    ...
```

## Debugging

### Enable Verbose Output

```python
# In your solver
import logging
logger = logging.getLogger(__name__)

logger.info(f"Creating mesh with {nx}x{ny}x{nz} cells")
logger.debug(f"Reynolds number: {re}")
logger.warning("Large time step may cause instability")
```

### Check Generated Files

```python
# Verify file generation
from fluidsimfoam.foam_input_files import parse

control_dict_path = sim.path_run / "system/controlDict"
tree = parse(control_dict_path.read_text())
print(tree)  # Check parsed structure
```

### Use IPython for Interactive Debugging

```python
# Add to your script
import IPython; IPython.embed()

# Or use ipdb
import ipdb; ipdb.set_trace()
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install OpenFOAM
        run: |
          sudo add-apt-repository ppa:openfoam/openfoam
          sudo apt-get update
          sudo apt-get install openfoam
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest tests/ --cov
```

## Common Pitfalls

### ❌ Don't

```python
# Don't modify params after Simul creation
params = Simul.create_default_params()
sim = Simul(params)
params.end_time = 100  # Too late!

# Don't use absolute paths in params
params.my_file = "/home/user/data.txt"  # Not portable

# Don't mix Python and shell string formatting
command = f"mpirun -np {n_cores} solver"  # Use invoke tasks instead
```

### ✅ Do

```python
# Set all params before creating Simul
params = Simul.create_default_params()
params.end_time = 100
sim = Simul(params)

# Use relative paths or Path objects
from pathlib import Path
params.my_file = Path("data/input.txt")

# Use the Make interface
sim.make.exec("run")
```

## Summary Checklist

- [ ] Organize project with clear directory structure
- [ ] Use version control (git/hg) properly
- [ ] Create parameter factories for common configs
- [ ] Write tests for your solver
- [ ] Document parameters and methods
- [ ] Prefer programmatic mesh generation
- [ ] Use Python for complex initial conditions
- [ ] Create descriptive run names for parametric studies
- [ ] Validate parameters before simulation
- [ ] Set up CI/CD for automated testing
- [ ] Profile performance for optimization
- [ ] Handle errors gracefully
- [ ] Keep OpenFOAM compatibility in mind

## Further Reading

- [Architecture Overview](architecture.md)
- [API Documentation](autosum.rst)
- [Tutorial Examples](tutorials.md)
- [Contributing Guide](CONTRIBUTING.md)
