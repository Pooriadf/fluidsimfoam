# Frequently Asked Questions (FAQ)

## General Questions

### What is Fluidsimfoam?

Fluidsimfoam is a Python framework that provides a modern workflow for OpenFOAM simulations. It's not a replacement for OpenFOAM but rather a tool to:
- Automate simulation workflows
- Generate input files programmatically
- Manage parameters systematically
- Facilitate parametric studies

### Do I still need OpenFOAM installed?

**Yes!** Fluidsimfoam requires OpenFOAM to be installed and properly sourced. Fluidsimfoam doesn't reimplement OpenFOAM—it manages workflows and generates input files that OpenFOAM commands then process.

### Is Fluidsimfoam compatible with my OpenFOAM version?

Fluidsimfoam targets OpenFOAM v2206 but should work with most recent versions (v1912+). The generated files are standard OpenFOAM format, so compatibility is generally good. Solver-specific features may vary.

### How is this different from PyFoam?

| Feature | Fluidsimfoam | PyFoam |
|---------|-------------|---------|
| **Focus** | Workflow automation, parametric studies | Utilities, case manipulation |
| **Approach** | Python-first design | Python wrapper around foam tools |
| **Parameters** | Hierarchical params object | Dictionary-based |
| **Solvers** | Plugin architecture | Single package |
| **Mesh generation** | Programmatic API | File manipulation |

Both tools are complementary and can be used together.

## Installation & Setup

### How do I install Fluidsimfoam?

```bash
# For users
pip install fluidsimfoam

# For developers (from GitHub fork)
git clone https://github.com/pooriadf/fluidsimfoam
cd fluidsimfoam
pip install -e .

# Or from official Heptapod repository
hg clone https://foss.heptapod.net/fluiddyn/fluidsimfoam
cd fluidsimfoam
pip install -e .
```

### I get "OpenFOAM not found" errors

Make sure OpenFOAM is sourced in your shell:

```bash
# For OpenFOAM.org
source /opt/openfoam10/etc/bashrc

# For OpenFOAM.com
source /usr/lib/openfoam/openfoam2212/etc/bashrc
```

Add this to your `~/.bashrc` to make it permanent.

### Can I use Fluidsimfoam on Windows?

OpenFOAM primarily runs on Linux. Options for Windows:
- **WSL2** (Windows Subsystem for Linux) - Recommended
- **Docker** - Run OpenFOAM in containers
- **Virtual Machine** - Full Linux installation

Fluidsimfoam itself is cross-platform Python code.

### Installation fails with permission errors

Use one of these approaches:

```bash
# Option 1: User installation
pip install --user fluidsimfoam

# Option 2: Virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fluidsimfoam

# Option 3: Conda environment
conda create -n fluidsimfoam python=3.10
conda activate fluidsimfoam
pip install fluidsimfoam
```

## Usage Questions

### How do I create my first simulation?

See the [Quick Start Guide](quickstart.md) for a complete walkthrough. Basic steps:

```python
from fluidsimfoam_tgv import Simul

params = Simul.create_default_params()
params.control_dict.end_time = 1.0
sim = Simul(params)
```

### Where are my simulation files created?

By default, in `$FLUIDDYN_PATH_SCRATCH` or a system temp directory. The path is printed when the simulation is created:

```
path_run: /path/to/simulation/directory
```

Control the location with:

```python
params.output.sub_directory = "my_study/case1"
```

### How do I load an existing simulation?

```python
from fluidsimfoam import load

sim = load("/path/to/simulation/directory")
```

Or use the command-line tool:

```bash
cd /path/to/simulation/directory
fluidsimfoam-ipy-load
```

### Can I modify parameters after creating the simulation?

No. Parameters must be set before creating the `Simul` object:

```python
# Correct
params = Simul.create_default_params()
params.end_time = 100.0
sim = Simul(params)

# Wrong - too late!
sim = Simul(params)
params.end_time = 100.0  # This won't affect the simulation
```

### How do I run parametric studies?

Use a loop to create multiple simulations:

```python
for reynolds in [100, 500, 1000]:
    params = Simul.create_default_params()
    params.short_name_type_run = f"re{reynolds}"
    params.transport_properties.nu = 1.0 / reynolds
    
    sim = Simul(params)
    # sim.make.exec("run")
```

## Solver Development

### How do I create a custom solver?

Use the initiation tool:

```bash
fluidsimfoam-initiate-solver mysolver -c /path/to/openfoam/case
```

This creates a `fluidsimfoam-mysolver` package. Customize the `output.py` file to add your specific logic.

### What's the difference between a "Fluidsim solver" and an "OpenFOAM solver"?

- **OpenFOAM solver**: C++ executable (e.g., `icoFoam`, `simpleFoam`)
- **Fluidsim solver**: Python package describing a set of simulations

A Fluidsim solver uses OpenFOAM solvers internally but adds Python-based workflow management.

### How do I add custom parameters?

In your solver's `Output` class:

```python
@classmethod
def _complete_params_with_default(cls, params):
    super()._complete_params_with_default(params)
    
    params._set_child(
        "my_custom",
        attribs={
            "parameter1": 1.0,
            "parameter2": "value"
        }
    )
```

### Can I use Jinja2 templates?

Yes! Create template files in your solver's `templates/` directory:

```python
# In output.py
from jinja2 import Template

def _make_tree_controlDict(self, params):
    template = Template(self.read_template("controlDict.jinja2"))
    return template.render(**params._make_dict())
```

## Mesh Generation

### How do I create a mesh programmatically?

Use the `BlockMeshDict` API:

```python
from fluidsimfoam.foam_input_files.blockmesh import (
    BlockMeshDict, Vertex, HexBlock, SimpleGrading
)

def _make_tree_blockMeshDict(self, params):
    bmd = BlockMeshDict()
    
    # Add vertices
    v0 = bmd.add_vertex(0, 0, 0, "v0")
    # ... more vertices
    
    # Add blocks
    block = bmd.add_hexblock(
        ["v0", "v1", "v2", "v3", "v4", "v5", "v6", "v7"],
        (nx, ny, nz),
        "block0"
    )
    
    # Add boundaries
    bmd.add_boundary("inlet", "patch", [...])
    
    return bmd
```

### Can I use snappyHexMesh?

Yes, but you'll need to set it up manually or use templates. Fluidsimfoam's `BlockMeshDict` API is specifically for `blockMesh`. For `snappyHexMesh`, you can:

1. Generate the configuration files using templates
2. Use the `Make` interface to run `snappyHexMesh`
3. See the `fluidsimfoam-multi-region-snappy` example

### How do I refine the mesh near boundaries?

Use `EdgeGrading` for non-uniform cell distribution:

```python
from fluidsimfoam.foam_input_files.blockmesh import EdgeGrading

grading = EdgeGrading([
    (0.2, 0.3, 4),    # 20% of length, 30% of cells, expansion ratio 4
    (0.6, 0.4, 1),    # 60% of length, 40% of cells, uniform
    (0.2, 0.3, 0.25)  # 20% of length, 30% of cells, contraction
])

block = HexBlock(..., grading=grading)
```

## Initial Conditions

### How do I set initial conditions?

Override the field generation methods in your `Output` class:

```python
def _make_tree_u(self, params):
    field = VolVectorField("U", "m/s")
    
    # Set boundaries
    field.set_boundary("inlet", "fixedValue", value=(1, 0, 0))
    field.set_boundary("outlet", "zeroGradient")
    field.set_boundary("walls", "noSlip")
    
    # Set internal field
    x, y, z = self.sim.oper.get_cells_coords()
    vx = np.ones_like(x)
    vy = np.zeros_like(y)
    vz = np.zeros_like(z)
    field.set_values(vx, vy, vz)
    
    return field
```

### Python vs CodeStream for initial conditions?

**Use Python when:**
- You need NumPy/SciPy
- Debugging is important
- Fields depend on parameters
- Complex logic required

**Use CodeStream when:**
- Performance is critical
- Using OpenFOAM functions
- Compatibility with existing code

### How do I restart from a previous simulation?

This is a planned feature. Current workaround:

```python
params.control_dict.start_from = "latestTime"
params.control_dict.start_time = "latestTime"

# Copy previous results to new case
import shutil
shutil.copytree(prev_sim_path / "processor0", new_sim_path / "processor0")
```

## Troubleshooting

### My simulation doesn't start

Check:
1. OpenFOAM is sourced: `which blockMesh`
2. Files were generated: `ls $path_run/system`
3. Check logs: `cat $path_run/log*.txt`
4. Validate mesh: `blockMesh -case $path_run`

### Parser errors when reading OpenFOAM files

The parser supports most OpenFOAM syntax but may fail on:
- Very complex `#codeStream` blocks
- Unusual macro definitions
- Custom preprocessor directives

Solutions:
- Simplify the file
- Use the "advanced" grammar: `parse(text, grammar="advanced")`
- Report the issue with a minimal example

### "Module not found" errors

Ensure the solver package is installed:

```bash
# If using an example solver
pip install -e doc/examples/fluidsimfoam-tgv

# For your custom solver
cd my-solver-package
pip install -e .
```

### Simulation runs but produces wrong results

Debug checklist:
1. **Verify mesh**: `paraFoam` and visually inspect
2. **Check boundary conditions**: Print generated field files
3. **Validate parameters**: Print `sim.params`
4. **Compare with baseline**: Run equivalent pure OpenFOAM case
5. **Check numerics**: `fvSchemes`, `fvSolution` settings

### How do I debug file generation?

```python
# Print generated file content
output = Output(sim)
tree = output._make_tree_controlDict(params)
print(tree.format())

# Or check the actual file
control_dict_path = sim.path_run / "system/controlDict"
print(control_dict_path.read_text())
```

## Performance

### How can I speed up simulations?

1. **Use parallel execution**:
   ```python
   params.decompose_par_dict.n_subdomains = 4
   ```

2. **Optimize mesh**: Not too fine, appropriate refinement
3. **Adjust time stepping**: Larger `deltaT` if stable
4. **Use efficient solvers**: Check `fvSolution` settings
5. **Profile**: Find bottlenecks in your Python code

### Can I run on HPC clusters?

Yes! Fluidsimfoam generates standard OpenFOAM cases that can be submitted to job schedulers:

```bash
# Generate case with Fluidsimfoam
python setup_simulation.py

# Submit to SLURM
sbatch run_openfoam.slurm
```

### Does Fluidsimfoam add overhead?

File generation adds minimal overhead (seconds). The actual simulation runs at native OpenFOAM speed since Fluidsimfoam only generates input files—it doesn't touch the solver execution.

## Data Analysis

### How do I read field data?

```python
from fluidsimfoam.foam_input_files.fields import VolVectorField

# Read a field file
field = VolVectorField.from_path(sim.path_run / "1.0/U")

# Get components
vx, vy, vz = field.get_components()
```

### Can I use ParaView?

Yes! Fluidsimfoam generates standard OpenFOAM cases:

```bash
# Create .foam file
touch case.foam

# Open in ParaView
paraview case.foam
```

### How do I extract specific data?

OpenFOAM utilities work normally:

```bash
# Sample along a line
postProcess -func sampleDict

# Compute forces
postProcess -func forces

# Or use Python with fluidfoam
pip install fluidfoam
```

## Contributing

### How can I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md). Ways to help:
- Report bugs
- Improve documentation
- Add examples
- Develop new solvers
- Fix issues

### Where should I report bugs?

Open an issue on [Heptapod](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/issues) with:
- Fluidsimfoam version (`fluidsimfoam-info`)
- OpenFOAM version
- Minimal reproducible example
- Error messages and logs

### Can I use GitHub instead of Heptapod?

The official repository is on [Heptapod](https://foss.heptapod.net/fluiddyn/fluidsimfoam) (Mercurial). 

A GitHub mirror/fork is available at [github.com/pooriadf/fluidsimfoam](https://github.com/pooriadf/fluidsimfoam) for those who prefer Git workflows.

## License & Citation

### What's the license?

BSD-3-Clause. See [LICENSE](../LICENSE) file.

### How do I cite Fluidsimfoam?

```bibtex
@software{fluidsimfoam,
  author = {Augier, Pierre and others},
  title = {Fluidsimfoam: Python framework for OpenFOAM},
  url = {https://foss.heptapod.net/fluiddyn/fluidsimfoam},
  version = {0.0.7},
  year = {2023}
}
```

## Still Have Questions?

- Check the [documentation](https://fluidsimfoam.readthedocs.io)
- Look at [examples](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples)
- Open an [issue](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/issues)
- Contact the maintainers
