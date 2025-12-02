# Architecture Overview

This document provides a high-level overview of Fluidsimfoam's architecture and design principles.

## Design Philosophy

Fluidsimfoam is designed around three core principles:

1. **Non-invasive**: Works alongside OpenFOAM without replacing or modifying it
2. **Pythonic**: Leverages Python's strengths for parametrization and automation
3. **Reproducible**: Parameters and configurations are explicitly stored and version-controlled

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Fluidsimfoam Layer                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Simul      │  │    Output    │  │  Operators   │     │
│  │   (Solver)   │  │ (File Gen)   │  │   (Mesh)     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │              │
│  ┌──────┴─────────────────┴──────────────────┴───────┐     │
│  │           Parameters (params object)              │     │
│  └───────────────────────────────┬───────────────────┘     │
└──────────────────────────────────┼──────────────────────────┘
                                   │
┌──────────────────────────────────┼──────────────────────────┐
│              File System Layer   │                          │
├──────────────────────────────────┼──────────────────────────┤
│  ┌────────────┐  ┌────────────┐ │ ┌────────────┐          │
│  │  system/   │  │ constant/  │ │ │    0/      │          │
│  │ (configs)  │  │ (physics)  │ │ │  (init)    │          │
│  └────────────┘  └────────────┘ │ └────────────┘          │
└──────────────────────────────────┼──────────────────────────┘
                                   │
┌──────────────────────────────────┼──────────────────────────┐
│               OpenFOAM Layer     ▼                          │
├──────────────────────────────────────────────────────────────┤
│  blockMesh → setFields → decomposePar → solver → postProc  │
└──────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Simul (Solver Class)

**Purpose**: Main entry point for creating and managing simulations

**Responsibilities**:
- Initialize simulation environment
- Coordinate between components
- Manage simulation lifecycle

**Key Methods**:
- `create_default_params()` - Generate parameter template
- `__init__(params)` - Set up simulation from parameters
- `stop_time_loop()` - Gracefully stop running simulations

**Example**:
```python
from fluidsimfoam_tgv import Simul

params = Simul.create_default_params()
params.control_dict.end_time = 10.0
sim = Simul(params)
```

### 2. Parameters

**Purpose**: Hierarchical configuration management

**Features**:
- Type-safe parameter storage
- XML serialization for reproducibility
- Nested structure matching OpenFOAM file organization
- Special character protection (parentheses, dots, etc.)

**Structure**:
```python
params
├── control_dict
│   ├── application
│   ├── start_time
│   ├── end_time
│   └── delta_t
├── fv_solution
│   ├── solvers
│   │   ├── p
│   │   └── U
│   └── PISO/SIMPLE
├── block_mesh_dict
│   ├── nx, ny, nz
│   └── lx, ly, lz
└── transport_properties
    └── nu
```

### 3. Output

**Purpose**: Manage file generation and simulation output

**Subcomponents**:
- `InputFiles` - Generate OpenFOAM configuration files
- `Fields` - Read and write field data
- `Log` - Parse and analyze solver output

**File Generators**:
```python
class Output:
    def _make_tree_u(self, params):
        # Generate initial velocity field
        field = VolVectorField("U", "m/s")
        field.set_boundary("inlet", "fixedValue", value=(1, 0, 0))
        return field
```

### 4. Operators

**Purpose**: Mesh operations and geometric queries

**Capabilities**:
- Extract cell center coordinates
- Compute mesh statistics
- Interface with OpenFOAM mesh tools

**Example**:
```python
x, y, z = sim.oper.get_cells_coords()
# Use coordinates for custom field initialization
```

### 5. Make (Build System)

**Purpose**: Execute OpenFOAM commands via invoke tasks

**Commands**:
- `polymesh` - Generate mesh
- `run` - Launch solver
- `clean` - Remove generated files

**Usage**:
```python
sim.make.exec("polymesh")  # Run blockMesh
sim.make.exec("run")       # Run solver
```

## Data Flow

### Simulation Creation Flow

```
1. User creates Parameters
   ↓
2. Simul.__init__(params)
   ↓
3. Output generates input files
   ├── controlDict (system/)
   ├── fvSchemes (system/)
   ├── fvSolution (system/)
   ├── blockMeshDict (system/)
   ├── transportProperties (constant/)
   └── Field files (0/)
   ↓
4. Files written to path_run
   ↓
5. OpenFOAM commands executed
```

### Simulation Loading Flow

```
1. fluidsimfoam.load(path_dir)
   ↓
2. Read params_simul.xml
   ↓
3. Identify solver from params
   ↓
4. Import solver class
   ↓
5. Recreate Simul object
   ↓
6. User accesses data via sim.output.fields
```

## File Parsing System

Fluidsimfoam includes a sophisticated parser for OpenFOAM files.

**Architecture**:
```
OpenFOAM File (text)
        ↓
    Lark Parser (grammar.lark)
        ↓
   Parse Tree (AST)
        ↓
FoamTransformer (AST → Python objects)
        ↓
Python Dict/List (FoamInputFile)
```

**AST Node Types**:
- `FoamInputFile` - Complete file
- `Dict` - OpenFOAM dictionary `{ }`
- `List` - OpenFOAM list `( )`
- `DimensionSet` - Dimensions `[ ]`
- `CodeStream` - C++ code blocks `#codeStream { }`
- `Value` - Primitive values (numbers, strings)

## Plugin System (Solvers)

Each solver is a separate Python package following this structure:

```
fluidsimfoam-<name>/
├── pyproject.toml
├── src/
│   └── fluidsimfoam_<name>/
│       ├── __init__.py         # Simul and InfoSolver classes
│       ├── output.py           # Custom Output class
│       └── templates/          # Jinja2 templates (optional)
│           ├── tasks.py        # Invoke tasks
│           └── *.jinja2        # Template files
└── tests/
    └── test_<name>.py
```

**Extension Points**:

1. **Custom Output Class**: Override file generation methods
2. **Custom Parameters**: Add solver-specific parameters
3. **Custom Operators**: Extend mesh operations
4. **Template System**: Use Jinja2 for dynamic files

## Helper Classes

### 1. BlockMesh Generator

Programmatic `blockMeshDict` creation:

```python
from fluidsimfoam.foam_input_files.blockmesh import BlockMeshDict

bmd = BlockMeshDict()
bmd.add_vertex(0, 0, 0, "origin")
# ... build mesh structure
bmd.format()  # Generate OpenFOAM text
```

### 2. Field Helpers

Type-safe field file creation:

```python
from fluidsimfoam.foam_input_files.fields import VolVectorField

field = VolVectorField("U", "m/s")
field.set_internal_field(uniform=(1, 0, 0))
field.set_boundary("inlet", "fixedValue", value=(1, 0, 0))
```

### 3. Helper Classes for Config Files

```python
ControlDictHelper()      # system/controlDict
FvSchemesHelper()        # system/fvSchemes
FvSolutionHelper()       # system/fvSolution (planned)
DecomposeParDictHelper() # system/decomposeParDict
ConstantFileHelper()     # constant/* files
```

## Threading and MPI Support

**Parallel Execution**:
- Automatic MPI detection via `decomposeParDict`
- Thread-safe parameter handling
- Rank-aware output generation

**Example**:
```python
params.decompose_par_dict.n_subdomains = 4
params.decompose_par_dict.method = "scotch"
sim = Simul(params)
# Fluidsimfoam handles MPI invocation
```

## Extension Mechanism

### Creating Custom Helpers

```python
from fluidsimfoam.foam_input_files import ConstantFileHelper

class MyPropertiesHelper(ConstantFileHelper):
    def __init__(self):
        super().__init__(
            "myProperties",
            default_dict={
                "myParameter": 1.0,
                "myVector": "(0 0 0)"
            }
        )
```

### Customizing File Generation

```python
class OutputCustom(Output):
    def _make_tree_blockMeshDict(self, params):
        # Custom mesh generation
        bmd = BlockMeshDict()
        # ... build mesh based on params
        return bmd.format()
```

## Testing Infrastructure

**Test Utilities**:
- `skipif_executable_not_available` - Skip if tool missing
- `skipif_openfoam_too_old` - Version checking
- Mock simulation environments

**Test Categories**:
1. Parser tests - Verify OpenFOAM file parsing
2. Generator tests - Check file generation
3. Integration tests - Full simulation workflows
4. Regression tests - Compare with saved cases

## Performance Considerations

**Optimization Strategies**:
1. Lazy file generation - Only create files when needed
2. Cached parsing - Parser results are reusable
3. Subprocess optimization - Efficient command execution
4. Memory-mapped I/O - For large field files (planned)

## Security Model

**Safe Practices**:
- No arbitrary code execution from config files (except explicit `codeStream`)
- Path validation for file operations
- Sandboxed subprocess execution
- Protected parameter storage

## Future Directions

**Planned Enhancements**:
1. Enhanced visualization integration (PyVista, Matplotlib)
2. Automated restarts and checkpointing
3. Advanced post-processing pipeline
4. Web-based monitoring dashboard
5. Cloud execution support
6. Optimization framework integration

## Contributing to Architecture

When extending Fluidsimfoam:

1. **Follow the Solver Pattern**: Create new solvers as separate packages
2. **Extend, Don't Replace**: Inherit from base classes
3. **Document Parameters**: Use clear docstrings in `_complete_params_*` methods
4. **Test Thoroughly**: Add tests for new components
5. **Maintain Compatibility**: Ensure generated files work with target OpenFOAM versions

## References

- [Fluidsim Core Documentation](https://fluidsim.readthedocs.io)
- [OpenFOAM User Guide](https://www.openfoam.com/documentation/user-guide)
- [Lark Parser](https://lark-parser.readthedocs.io)
