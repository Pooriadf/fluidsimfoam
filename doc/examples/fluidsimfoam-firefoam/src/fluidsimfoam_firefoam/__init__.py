from fluidsimfoam.info import InfoSolver
from fluidsimfoam.solvers.base import SimulFoam

__all__ = ["Simul"]


class InfoSolverFireFoam(InfoSolver):
    def _init_root(self):
        super()._init_root()
        self.module_name = "fluidsimfoam_firefoam"
        self.class_name = "Simul"
        self.short_name = "firefoam"

        self.classes.Output.module_name = "fluidsimfoam_firefoam.output"
        self.classes.Output.class_name = "OutputFireFoam"


class Simul(SimulFoam):
    InfoSolver = InfoSolverFireFoam
