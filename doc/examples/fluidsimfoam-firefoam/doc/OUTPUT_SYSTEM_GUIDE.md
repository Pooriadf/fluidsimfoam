# Understanding the Output System in fluidsimfoam

## Overview

The fluidsimfoam output system is designed to:
1. Generate OpenFOAM case files from parameters
2. Manage simulation execution
3. Read field data from completed simulations
4. Visualize and analyze results

## How Output Works

### 1. Output Class Structure

The `Output` class (in `src/fluidsimfoam/output/base.py`) is the main interface:

```python
class Output(OutputCore):
    name_variables = ["p", "U"]           # Field variables
    name_constant_files = [...]           # Files in constant/
    name_system_files = [...]             # Files in system/
```

### 2. Fields Class for Reading Data

The `Fields` class (in `src/fluidsimfoam/output/fields.py`) handles reading and plotting:

```python
# Key methods:
- get_saved_times()           # List all available time directories
- read_field(name, time)      # Read a field file
- plot_field(name, time)      # Basic plotting
- plot_contour(variable, ...)  # 3D contour plots (requires pyvista)
- plot_boundary(name, ...)     # Boundary visualization
- reconstruct_par(fields, time) # Reconstruct parallel cases
```

### 3. Reading an Existing Case

The current system requires a `Simul` object to use the output system. For reading existing cases without creating a new simulation, we created a **workaround** in the fireFoam example:

#### CaseLoader Utility

See `doc/examples/fluidsimfoam-firefoam/doc/example_load_case.py`

```python
class CaseLoader:
    """Lightweight wrapper to use Fields class without full Simul"""
    
    def __init__(self, case_path, nsubdoms=1):
        # Create minimal sim-like structure
        self.output = SimpleOutput(case_path, nsubdoms)
        self.fields = Fields(self.output)
    
    def read_field(self, name, time="last"):
        return self.fields.read_field(name, time)
```

This creates the minimum structure needed by the `Fields` class:
- `output.path_run` → case directory
- `output.sim.params.parallel.nsubdoms` → number of processors

## Usage Patterns

### A. Creating and Running a New Case

```python
from fluidsimfoam_firefoam import Simul

params = Simul.create_default_params()
params.output.sub_directory = "my_case"

sim = Simul(params)  # Creates case structure
sim.make.exec("run")  # Runs the simulation
```

### B. Analyzing an Existing Case

```python
from example_load_case import CaseLoader

# Load completed case
case = CaseLoader("/path/to/case", nsubdoms=10)

# Read fields
T = case.read_field("T", time_approx="last")
U = case.read_field("U", time_approx="last")

# Get data arrays
T_array = T.get_array()
U_array = U.get_array()

print(f"Temperature: {T_array.min():.2f} - {T_array.max():.2f} K")
```

### C. Plotting Results

```python
# For parallel cases, reconstruct first
case.fields.reconstruct_par(fields=["T", "U"], latest_time=True)

# Then plot (requires pyvista)
case.fields.plot_contour(
    variable="T",
    mesh_opacity=0.1,
    show=True
)

case.fields.plot_boundary(
    name="inlet",
    color="r",
    show=True
)
```

## Key Components

### Output.path_run
The directory where the case is located. For new simulations, this is automatically created. For existing cases, point to the existing directory.

### Fields.get_saved_times()
Scans the case directory for numeric directories (0, 1, 2, etc.) representing time steps.

### Fields.read_field()
Reads OpenFOAM field files using `read_field_file()` parser. Returns an object with:
- `.time` - the time value
- `.get_array()` - numpy array of field values

### Fields.reconstruct_par()
For parallel cases with `processor0/`, `processor1/`, etc., this calls `reconstructPar` to merge results into unified time directories.

## Modifications for Your Use Case

Based on your request "I want to change it, that it can read a case and be able to plot the figures", we've created:

### 1. CaseLoader Class
A simplified interface to read existing cases without creating a Simul object.

**Location**: `doc/examples/fluidsimfoam-firefoam/doc/example_load_case.py`

### 2. Example Script
A complete working example that:
- Loads your fireFoam case
- Reads temperature, velocity, species fields
- Shows statistics (min, max, mean)
- Demonstrates plotting options

**Location**: Same file, `main()` function

### 3. Integration with FireFoam Package
The fireFoam example is now a complete fluidsimfoam package that:
- Registers as a solver plugin
- Contains your complete OpenFOAM case as templates
- Can be used to create new cases or analyze existing ones

## Future Enhancements

To make reading existing cases even easier, consider:

### Option 1: Add to Output class
```python
class Output:
    @classmethod
    def from_case(cls, case_path, nsubdoms=1):
        """Create Output from existing case without Simul"""
        # Return minimal Output object for reading
```

### Option 2: Standalone reader module
```python
from fluidsimfoam.readers import CaseReader

reader = CaseReader("/path/to/case")
reader.plot("T")
```

## Summary

✅ **Current Capability**: The output system can read and plot from existing cases using the `Fields` class

✅ **What We Added**: A `CaseLoader` utility that simplifies this process

✅ **How to Use**: 
1. Use `CaseLoader` from the example
2. Call `read_field()` to get field data
3. Use plotting methods from `Fields` class

✅ **Your Case**: Now packaged as `fluidsimfoam-firefoam` example with working read/plot functionality
