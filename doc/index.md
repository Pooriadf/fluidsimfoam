# Fluidsimfoam Documentation

Fluidsimfoam is a Python framework for [OpenFOAM] that enables modern, Python-based workflows for CFD simulations. It provides tools to:

- **Describe** sets of similar simulations in Python
- **Organize** parameters hierarchically and reproducibly
- **Generate** OpenFOAM input files programmatically
- **Launch** and restart simulations with simple commands
- **Analyze** results and produce figures/movies

```{list-table}
* - Repository
  - <https://foss.heptapod.net/fluiddyn/fluidsimfoam>

* - Version
  - [{{ release}}](https://pypi.org/project/fluidsimfoam/)

* - License
  - BSD-3-Clause
```

## Getting Started

New to Fluidsimfoam? Start here:

1. [Introduction](intro.md) - What is Fluidsimfoam and why use it?
2. [Installation](install.md) - Get Fluidsimfoam up and running
3. [Quick Start](quickstart.md) - Create your first simulation in minutes
4. [Tutorials](tutorials.md) - Step-by-step examples

## User Guide

```{toctree}
---
caption: User Guide
maxdepth: 2
---
intro
install
quickstart
tutorials
architecture
best_practices
faq
```

```{toctree}
---
caption: Python API
maxdepth: 2
---
api_examples
autosum.rst
```

```{toctree}
---
caption: Help & Reference
maxdepth: 1
---
CHANGELOG
CONTRIBUTING
AUTHORS
dev/index.md
```

## Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`

[openfoam]: https://openfoam.org/
