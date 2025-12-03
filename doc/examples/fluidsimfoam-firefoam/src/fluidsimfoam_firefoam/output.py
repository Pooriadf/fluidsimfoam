from fluidsimfoam.output import Output


class OutputFireFoam(Output):
    """Output class for fireFoam combustion simulations"""
    
    name_variables = [
        "U", "p", "p_rgh", "T", 
        "C7H16", "O2", "N2",  # Species
        "alphat", "k", "nut",  # Turbulence
        "G", "IDefault",  # Radiation
    ]
    
    name_system_files = [
        "blockMeshDict",
        "controlDict",
        "decomposeParDict",
        "fvSchemes",
        "fvSolution",
        "snappyHexMeshDict",
        "meshQualityDict",
    ]
    
    name_constant_files = [
        "g",
        "transportProperties",
        "thermophysicalProperties",
        "combustionProperties",
        "radiationProperties",
        "boundaryRadiationProperties",
        "thermo.compressibleGas",
        "reactions",
        "additionalControls",
        "surfaceFilmProperties",
        "reactingCloud1Properties",
        "pyrolysisZones",
        "hRef",
    ]

    _helper_control_dict = Output._helper_control_dict.new(
        """
        application     fireFoam;
        endTime         150;
        deltaT          0.001;
        writeControl    adjustable;
        writeInterval   1;
        adjustTimeStep  yes;
        maxCo           0.6;
        maxDi           10.0;
        maxDeltaT       0.01;
    """
    )

    @classmethod
    def _complete_params_block_mesh_dict(cls, params):
        """Complete parameters for blockMeshDict"""
        super()._complete_params_block_mesh_dict(params)
        params.block_mesh_dict._update_attribs(
            {
                "nx": 50,
                "ny": 20,
                "nz": 20,
                "lx": 36.5,
                "ly": 12.0,
                "lz": 17.0,
                "scale": 1.0,
            }
        )
