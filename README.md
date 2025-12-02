<div align="center">

# Fluidsimfoam

[![PyPI](https://img.shields.io/pypi/v/fluidsimfoam)](https://pypi.org/project/fluidsimfoam/)
[![Documentation Status](https://readthedocs.org/projects/fluidsimfoam/badge/?version=latest)](https://fluidsimfoam.readthedocs.io/en/latest/?badge=latest)

**A Python framework for [OpenFOAM]**

</div>

<!-- start-intro -->

[OpenFOAM] is a highly popular open-source C++ [CFD] framework. With
Fluidsimfoam, we **design and propose a new Python-based workflow for OpenFOAM**.
Experienced OpenFOAM users will feel at home: Fluidsimfoam produces standard
OpenFOAM cases in the end, and it's always possible to return to the traditional
OpenFOAM workflow.

Fluidsimfoam serves as a workflow manager and Python wrapper for OpenFOAM. It
exclusively uses OpenFOAM commands in the background and is **NOT a rewrite of
OpenFOAM**!

## Key Use Cases

Fluidsimfoam is especially valuable for:

- **Automation** - Launch simulations for parametric studies and optimization workflows
- **Programmatic generation** - Create complex, parameterized input files (e.g., `blockMeshDict`) and initial conditions
- **Runtime control** - Programmatically manage simulations during execution ([example](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/scripts/2023sed-parametric))

Beyond these use cases, Fluidsimfoam is convenient for Python users tackling any
OpenFOAM workflow that doesn't require C++ programming.

## Why Fluidsimfoam?

Working with OpenFOAM typically involves writing and modifying numerous input files
to describe a simulation. The standard approach, as outlined in the official OpenFOAM
documentation, is to copy an existing simulation directory and manually edit the
input files.

With Fluidsimfoam, you can describe not just individual cases (as in the
[OpenFOAM tutorials]), but **entire sets of similar simulations**. These
simulation sets are defined in Python (optionally using [Jinja] templates)
within small Python packages we call "[Fluidsim] solvers".

> **Note:** A "[Fluidsim] solver" and an "OpenFOAM solver" are fundamentally different.
> A Fluidsim solver is a Python package that describes a set of simulations, while
> Fluidsimfoam enables you to create Fluidsim solvers that run on OpenFOAM.

As demonstrated in [our tutorials], Fluidsimfoam solvers make it simple to:

- Launch and restart simulations using Python scripts or terminal commands
- Load simulations, read parameters and data, and generate figures or movies

Several open-source solvers [are included in our repository](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples),
and creating your own solver from existing OpenFOAM cases is straightforward.
For example, to generate a solver from an existing case, run:

```sh
fluidsimfoam-initiate-solver cylinder -c $FOAM_TUTORIALS/basic/potentialFoam/cylinder
```

This command creates a `fluidsimfoam-cylinder` solver for running the
[Flow around a cylinder](https://www.openfoam.com/documentation/tutorial-guide/2-incompressible-flow/2.2-flow-around-a-cylinder)
tutorial. This solver can be easily enhanced to support parameterization and
programmatic file generation. For instance, the tutorial's mesh is generated using
the `blockMesh` utility with a complex `blockMeshDict` containing `#codeStream`
directives (requiring C++ code and compilation). **With Fluidsimfoam, you can skip
this step** and generate the `blockMeshDict` programmatically using an elegant
Python API with built-in parameter management.

## Usage Patterns

The recommended approach is to create or use a solver tailored to your specific
use case. Alternatively, you can leverage Fluidsimfoam's Python functions and
classes for common tasks such as:

- Parsing and writing input files
- Modifying field files
- Generating `blockMeshDict` files
- And more...

## Project Status

Fluidsimfoam is **functional and ready for use**, though still in active early
development. Some features remain to be implemented, such as
[restart utilities](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/issues/40)
and [automated figure/movie generation](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/issues/38).
Our documentation is evolving to better showcase the tool's full capabilities.

Our goal is to achieve feature parity with [Snek5000], our Fluidsim framework for
[Nek5000]. The [Snek5000] tutorials offer a preview of Fluidsimfoam's future
capabilities.

**Current target:** OpenFOAM v2206, though Fluidsimfoam solvers should work with
most recent OpenFOAM versions.

## Contributing

This is a **young project** and we welcome all forms of feedback and [contributions]!
Don't let the fact that we're not on GitHub stop you. If you find this project
interesting:

- ⭐ **Star** [our repository on Heptapod](https://foss.heptapod.net/fluiddyn/fluidsimfoam)
- 🐛 **Open issues** for [feedback, feature requests, or bug reports](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/issues)
- 👥 **Join as a core developer** - if you're passionate about OpenFOAM and Python, we'd love to have you!

[fluiddyn]: https://fluiddyn.readthedocs.io
[fluidsim]: https://fluidsim.readthedocs.io
[fluidfoam]: https://fluidfoam.readthedocs.io
[openfoam]: https://openfoam.org/
[OpenFOAM tutorials]: https://www.openfoam.com/documentation/tutorial-guide
[nek5000]: https://nek5000.mcs.anl.gov/
[snek5000]: https://snek5000.readthedocs.io
[Jinja]: https://jinja.palletsprojects.com
[contributions]: https://fluidsimfoam.readthedocs.io/en/latest/CONTRIBUTING.html
[our tutorials]: https://fluidsimfoam.readthedocs.io/en/latest/tutorials.html
[CFD]: https://en.wikipedia.org/wiki/Computational_fluid_dynamics

<!-- end-intro -->

See more in [Fluidsimfoam documentation](https://fluidsimfoam.readthedocs.org).

## Installation

<!-- start-install -->

### For Users

Install from PyPI:

```sh
pip install fluidsimfoam
```

### For Developers

We recommend installing Fluidsimfoam in a dedicated virtual environment using
[PDM]. First, install [PDM] (e.g., `pipx install pdm`), then run:

```sh
hg clone https://foss.heptapod.net/fluiddyn/fluidsimfoam
cd fluidsimfoam
pdm install
pdm venv activate
```

Alternatively, for an editable installation:

```sh
pip install -e .
```

[pdm]: https://pdm-project.org

<!-- end-install -->

## Related Projects

- **[Fluidfoam]** - Another [Fluiddyn] package for reading and plotting OpenFOAM
  data. Will be integrated with Fluidsimfoam.

- **[PyFoam]** - Python utilities for OpenFOAM ([PyPI](https://pypi.org/project/PyFoam/),
  [repo](http://hg.code.sf.net/p/openfoam-extend/PyFoam)). GNU GPL licensed, actively maintained.

- **[PythonFlu]** - Python bindings for OpenFOAM ([wiki](https://openfoamwiki.net/index.php/Contrib_pythonFlu))

- **[Swak4Foam]** - Popular utility collection for OpenFOAM, compatible with
  Fluidsimfoam solvers.

[PyFoam]: https://openfoamwiki.net/index.php/Contrib/PyFoam
[PythonFlu]: http://pythonflu.wikidot.com/
[Swak4Foam]: https://openfoamwiki.net/index.php/Contrib/swak4Foam
