# API Examples

This page provides practical code examples for common Fluidsimfoam operations.

## Table of Contents

- [Parameter Management](#parameter-management)
- [Mesh Generation](#mesh-generation)
- [Field Initialization](#field-initialization)
- [File Parsing](#file-parsing)
- [Simulation Control](#simulation-control)
- [Data Analysis](#data-analysis)

## Parameter Management

### Creating and Modifying Parameters

```python
from fluidsimfoam_tgv import Simul

# Create default parameters
params = Simul.create_default_params()

# Access nested parameters
print(params.control_dict.end_time)  # Output: 1.0

# Modify parameters
params.control_dict.end_time = 10.0
params.control_dict.delta_t = 0.01
params.control_dict.write_interval = 1.0

# Add custom attributes
params._set_attrib("my_parameter", 42)
params._set_child("my_section", attribs={"value1": 1.0, "value2": 2.0})
```

### Saving and Loading Parameters

```python
from pathlib import Path
from fluidsimfoam.params import Parameters

# Save parameters to XML
params.save(Path("my_params.xml"))

# Load parameters from XML
loaded_params = Parameters(path_file=Path("my_params.xml"))

# Convert to dictionary
params_dict = params._make_dict()
```

### Creating Parameter Templates

```python
def create_channel_params(reynolds, mesh_resolution="medium"):
    """Factory function for channel flow parameters."""
    params = Simul.create_default_params()
    
    # Physical setup
    params.transport_properties.nu = 1.0 / reynolds
    
    # Mesh resolution presets
    resolutions = {
        "coarse": (32, 16, 8),
        "medium": (64, 32, 16),
        "fine": (128, 64, 32)
    }
    nx, ny, nz = resolutions[mesh_resolution]
    params.block_mesh_dict.nx = nx
    params.block_mesh_dict.ny = ny
    params.block_mesh_dict.nz = nz
    
    # Time stepping
    params.control_dict.delta_t = 0.001
    params.control_dict.end_time = 100.0
    
    return params

# Usage
params = create_channel_params(reynolds=1000, mesh_resolution="fine")
```

## Mesh Generation

### Basic BlockMeshDict

```python
from fluidsimfoam.foam_input_files.blockmesh import (
    BlockMeshDict,
    Vertex,
    HexBlock,
    SimpleGrading,
)

# Create mesh dictionary
bmd = BlockMeshDict()
bmd.set_scale(1.0)

# Add vertices for a 2D channel (extruded in z)
bmd.add_vertex(0.0, 0.0, 0.0, "v0")
bmd.add_vertex(10.0, 0.0, 0.0, "v1")
bmd.add_vertex(10.0, 1.0, 0.0, "v2")
bmd.add_vertex(0.0, 1.0, 0.0, "v3")
bmd.add_vertex(0.0, 0.0, 0.1, "v4")
bmd.add_vertex(10.0, 0.0, 0.1, "v5")
bmd.add_vertex(10.0, 1.0, 0.1, "v6")
bmd.add_vertex(0.0, 1.0, 0.1, "v7")

# Create hex block
block = bmd.add_hexblock(
    ["v0", "v1", "v2", "v3", "v4", "v5", "v6", "v7"],
    (100, 20, 1),  # cells in x, y, z
    "channel",
    SimpleGrading(1, 1, 1)
)

# Add boundaries
bmd.add_boundary(
    "inlet",
    "patch",
    [[["v0", "v3", "v7", "v4"]]]
)
bmd.add_boundary(
    "outlet",
    "patch",
    [[["v1", "v2", "v6", "v5"]]]
)
bmd.add_boundary(
    "walls",
    "wall",
    [
        [["v0", "v1", "v5", "v4"]],  # bottom
        [["v3", "v2", "v6", "v7"]]   # top
    ]
)
bmd.add_boundary(
    "frontAndBack",
    "empty",
    [
        [["v0", "v1", "v2", "v3"]],  # back
        [["v4", "v5", "v6", "v7"]]   # front
    ]
)

# Generate OpenFOAM format
mesh_text = bmd.format()
print(mesh_text)
```

### Mesh with Grading

```python
from fluidsimfoam.foam_input_files.blockmesh import EdgeGrading

# Create grading for boundary layer refinement
# Format: (length_fraction, cell_fraction, expansion_ratio)
grading_y = EdgeGrading([
    (0.1, 0.3, 10),   # 10% length, 30% cells, expanding
    (0.8, 0.4, 1),    # 80% length, 40% cells, uniform
    (0.1, 0.3, 0.1)   # 10% length, 30% cells, contracting
])

block = bmd.add_hexblock(
    vertex_names,
    (nx, ny, nz),
    "block",
    SimpleGrading(1, grading_y, 1)  # grading only in y
)
```

### Parametric Mesh Generation

```python
def create_parametric_cylinder_mesh(radius, length, n_radial, n_axial):
    """Generate mesh for cylinder geometry."""
    import numpy as np
    
    bmd = BlockMeshDict()
    
    # Generate vertices in cylindrical coordinates
    n_theta = 8  # Octagonal approximation
    for i in range(n_theta):
        theta = 2 * np.pi * i / n_theta
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        
        # Inlet face
        bmd.add_vertex(x, y, 0, f"v_inlet_{i}")
        # Outlet face
        bmd.add_vertex(x, y, length, f"v_outlet_{i}")
    
    # Create blocks connecting vertices
    for i in range(n_theta):
        j = (i + 1) % n_theta
        vnames = [
            f"v_inlet_{i}", f"v_inlet_{j}",
            f"v_outlet_{j}", f"v_outlet_{i}",
            # ... add center vertices if needed
        ]
        bmd.add_hexblock(
            vnames,
            (n_radial, n_axial, 1),
            f"block_{i}",
            SimpleGrading(1, 1, 1)
        )
    
    return bmd
```

## Field Initialization

### Creating Velocity Fields

```python
from fluidsimfoam.foam_input_files.fields import VolVectorField

# Create velocity field
u_field = VolVectorField("U", "m/s")

# Set uniform internal field
u_field.set_internal_field(uniform=(1.0, 0.0, 0.0))

# Set boundary conditions
u_field.set_boundary("inlet", "fixedValue", value=(1.0, 0.0, 0.0))
u_field.set_boundary("outlet", "zeroGradient")
u_field.set_boundary("walls", "noSlip")
u_field.set_boundary("symmetry", "symmetryPlane")

# Write to file
output_path = Path("0/U")
u_field.write(output_path)
```

### Creating Scalar Fields

```python
from fluidsimfoam.foam_input_files.fields import VolScalarField

# Pressure field
p_field = VolScalarField("p", "m^2/s^2")
p_field.set_internal_field(uniform=0.0)
p_field.set_boundary("inlet", "zeroGradient")
p_field.set_boundary("outlet", "fixedValue", value=0.0)
p_field.set_boundary("walls", "zeroGradient")

# Temperature field
t_field = VolScalarField("T", "K")
t_field.set_internal_field(uniform=300.0)
t_field.set_boundary("inlet", "fixedValue", value=350.0)
t_field.set_boundary("outlet", "zeroGradient")
t_field.set_boundary("walls", "fixedValue", value=300.0)
```

### Using NumPy for Initial Conditions

```python
import numpy as np

# Get cell coordinates
x, y, z = sim.oper.get_cells_coords()

# Analytical velocity profile (Poiseuille flow)
u_max = 1.0
height = 1.0
vx = u_max * (1 - (2 * y / height) ** 2)
vy = np.zeros_like(vx)
vz = np.zeros_like(vx)

# Create field with computed values
u_field = VolVectorField("U", "m/s")
u_field.set_values(vx, vy, vz)
u_field.set_boundary("inlet", "fixedValue", value=(u_max, 0, 0))
u_field.set_boundary("outlet", "zeroGradient")
u_field.set_boundary("walls", "noSlip")
```

### Taylor-Green Vortex Initial Condition

```python
def initialize_taylor_green_vortex(sim, params):
    """Initialize Taylor-Green vortex flow."""
    x, y, z = sim.oper.get_cells_coords()
    
    # TGV analytical solution at t=0
    vx = np.sin(x) * np.cos(y) * np.cos(z)
    vy = -np.cos(x) * np.sin(y) * np.cos(z)
    vz = np.zeros_like(x)
    
    pressure = -0.25 * (np.cos(2*x) + np.cos(2*y)) * (np.cos(2*z) + 2)
    
    # Create fields
    u_field = VolVectorField("U", "m/s")
    u_field.set_values(vx, vy, vz)
    
    p_field = VolScalarField("p", "m^2/s^2")
    p_field.set_values(pressure)
    
    return u_field, p_field
```

## File Parsing

### Reading OpenFOAM Files

```python
from fluidsimfoam.foam_input_files import parse, dump
from pathlib import Path

# Read a file
file_path = Path("system/controlDict")
with open(file_path) as f:
    content = f.read()

# Parse to AST
tree = parse(content)

# Access data
print(tree["application"])           # Direct access
print(tree["startTime"])
print(tree["endTime"])

# Modify
tree["endTime"] = 100.0

# Write back
modified_content = dump(tree)
with open(file_path, 'w') as f:
    f.write(modified_content)
```

### Parsing Field Files

```python
from fluidsimfoam.foam_input_files.fields import VolVectorField, VolScalarField

# Read velocity field
u_field = VolVectorField.from_path(Path("0/U"))

# Access internal field
internal = u_field.internal_field
print(f"Internal field type: {type(internal)}")

# Get velocity components
vx, vy, vz = u_field.get_components()
print(f"Velocity shape: {vx.shape}")

# Read scalar field
p_field = VolScalarField.from_path(Path("0/p"))
pressure = p_field.internal_field
```

### Reading Binary Field Files

```python
# Fluidsimfoam automatically handles binary fields
field = VolVectorField.from_path(Path("100/U"))

# The internal field is automatically parsed from binary
# if the file is in binary format
vx, vy, vz = field.get_components()
```

## Simulation Control

### Creating and Running Simulations

```python
from fluidsimfoam_tgv import Simul

# Create simulation
params = Simul.create_default_params()
params.control_dict.end_time = 10.0
sim = Simul(params)

# Run mesh generation
sim.make.exec("polymesh")

# Run the solver
sim.make.exec("run")

# Clean up
sim.make.exec("clean")
```

### Stopping Simulations Gracefully

```python
import signal
import time

def run_with_timeout(sim, timeout_seconds):
    """Run simulation with timeout."""
    
    # Start simulation
    process = sim.make.exec_async("run")
    
    # Wait with timeout
    start_time = time.time()
    while process.poll() is None:
        if time.time() - start_time > timeout_seconds:
            print("Timeout reached, stopping simulation...")
            sim.stop_time_loop(stop_at="writeNow")
            break
        time.sleep(1.0)
    
    return process.returncode

# Usage
return_code = run_with_timeout(sim, timeout_seconds=3600)  # 1 hour
```

### Monitoring Simulation Progress

```python
from pathlib import Path
import time

def monitor_simulation(sim, check_interval=10):
    """Monitor simulation progress."""
    path_run = Path(sim.path_run)
    
    while True:
        # Get list of time directories
        time_dirs = sorted(
            [d.name for d in path_run.glob("*") if d.is_dir() and d.name[0].isdigit()],
            key=float
        )
        
        if time_dirs:
            current_time = time_dirs[-1]
            print(f"\rCurrent simulation time: {current_time}", end="")
        
        # Check if complete
        log_file = path_run / "log.icoFoam"  # Adjust solver name
        if log_file.exists():
            with open(log_file) as f:
                content = f.read()
                if "End" in content:
                    print("\nSimulation complete!")
                    break
        
        time.sleep(check_interval)

# Usage
monitor_simulation(sim)
```

## Data Analysis

### Loading Simulations

```python
from fluidsimfoam import load

# Load from directory
sim = load("/path/to/simulation")

# Access parameters
print(f"Reynolds number: {sim.params.transport_properties.nu}")
print(f"End time: {sim.params.control_dict.end_time}")

# Get simulation path
print(f"Simulation directory: {sim.path_run}")
```

### Reading Time Series Data

```python
from pathlib import Path

def get_time_directories(sim):
    """Get all time directories."""
    path_run = Path(sim.path_run)
    time_dirs = sorted(
        [d for d in path_run.glob("*") if d.is_dir() and d.name[0].isdigit()],
        key=lambda x: float(x.name)
    )
    return time_dirs

# Get all times
times = get_time_directories(sim)
print(f"Available times: {[t.name for t in times]}")

# Read field at each time
for time_dir in times:
    u_path = time_dir / "U"
    if u_path.exists():
        u_field = VolVectorField.from_path(u_path)
        vx, vy, vz = u_field.get_components()
        # Analyze velocity field
        print(f"Time {time_dir.name}: max velocity = {np.max(np.sqrt(vx**2 + vy**2 + vz**2))}")
```

### Computing Statistics

```python
import numpy as np

def compute_flow_statistics(sim):
    """Compute flow statistics from final time step."""
    # Get final time directory
    times = get_time_directories(sim)
    final_time = times[-1]
    
    # Read velocity
    u_field = VolVectorField.from_path(final_time / "U")
    vx, vy, vz = u_field.get_components()
    
    # Compute statistics
    velocity_magnitude = np.sqrt(vx**2 + vy**2 + vz**2)
    
    stats = {
        "mean_velocity": np.mean(velocity_magnitude),
        "max_velocity": np.max(velocity_magnitude),
        "min_velocity": np.min(velocity_magnitude),
        "std_velocity": np.std(velocity_magnitude),
    }
    
    return stats

# Usage
stats = compute_flow_statistics(sim)
print(stats)
```

### Visualization with Matplotlib

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_velocity_profile(sim, time="latest"):
    """Plot velocity profile."""
    # Load field
    if time == "latest":
        times = get_time_directories(sim)
        time_dir = times[-1]
    else:
        time_dir = Path(sim.path_run) / time
    
    u_field = VolVectorField.from_path(time_dir / "U")
    x, y, z = sim.oper.get_cells_coords()
    vx, vy, vz = u_field.get_components()
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Velocity magnitude
    vel_mag = np.sqrt(vx**2 + vy**2 + vz**2)
    im1 = ax1.tricontourf(x.flatten(), y.flatten(), vel_mag.flatten(), levels=20)
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    ax1.set_title('Velocity Magnitude')
    plt.colorbar(im1, ax=ax1)
    
    # Pressure (if available)
    p_path = time_dir / "p"
    if p_path.exists():
        p_field = VolScalarField.from_path(p_path)
        pressure = p_field.internal_field
        im2 = ax2.tricontourf(x.flatten(), y.flatten(), pressure.flatten(), levels=20)
        ax2.set_xlabel('x')
        ax2.set_ylabel('y')
        ax2.set_title('Pressure')
        plt.colorbar(im2, ax=ax2)
    
    plt.tight_layout()
    plt.savefig('velocity_field.png', dpi=150)
    plt.show()

# Usage
plot_velocity_profile(sim)
```

## Advanced Examples

### Custom Output Class

```python
from fluidsimfoam.output import Output
from fluidsimfoam.foam_input_files import VolVectorField, VolScalarField

class OutputCustom(Output):
    """Custom output with special initial conditions."""
    
    @classmethod
    def _complete_params_with_default(cls, params):
        super()._complete_params_with_default(params)
        
        # Add custom parameters
        params._set_child(
            "custom_ic",
            attribs={
                "velocity_scale": 1.0,
                "perturbation_amplitude": 0.1,
            }
        )
    
    def _make_tree_u(self, params):
        """Generate velocity field with perturbation."""
        field = VolVectorField("U", "m/s")
        
        # Get coordinates
        x, y, z = self.sim.oper.get_cells_coords()
        
        # Base flow + perturbation
        vx = params.custom_ic.velocity_scale * (
            1.0 + params.custom_ic.perturbation_amplitude * np.sin(2 * np.pi * x)
        )
        vy = np.zeros_like(vx)
        vz = np.zeros_like(vx)
        
        field.set_values(vx, vy, vz)
        field.set_boundary("inlet", "fixedValue", value=(1, 0, 0))
        field.set_boundary("outlet", "zeroGradient")
        field.set_boundary("walls", "noSlip")
        
        return field
```

### Parallel Execution Helper

```python
from concurrent.futures import ProcessPoolExecutor
import itertools

def run_parametric_study_parallel(param_ranges, max_workers=4):
    """Run parametric study in parallel."""
    
    def run_single_case(params_tuple):
        """Run a single case."""
        re, mesh_size = params_tuple
        
        params = create_channel_params(re, mesh_size)
        params.short_name_type_run = f"re{re}_mesh{mesh_size}"
        
        sim = Simul(params)
        sim.make.exec("run")
        
        return sim.path_run
    
    # Generate all parameter combinations
    param_combinations = list(itertools.product(*param_ranges.values()))
    
    # Run in parallel
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(run_single_case, param_combinations)
    
    return list(results)

# Usage
param_ranges = {
    "reynolds": [100, 500, 1000],
    "mesh_size": ["coarse", "medium"]
}
paths = run_parametric_study_parallel(param_ranges, max_workers=4)
```

For more examples, see:
- [Tutorials](tutorials.md)
- [Example solvers](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples)
- [Test files](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/tests)
