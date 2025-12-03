from pathlib import Path

from fluidsimfoam_firefoam import Simul

from fluidsimfoam.testing import skipif_executable_not_available

here = Path(__file__).absolute().parent


def test_create_params():
    """Test that we can create default parameters"""
    params = Simul.create_default_params()
    assert params is not None
    assert params.output is not None


def test_generate_base_case():
    """Test case generation without running simulation"""
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/firefoam"
    params.NEW_DIR_RESULTS = False  # Don't create new directory for testing
    params.parallel.method = "simple"
    params.parallel.nsubdoms = 10
    params.parallel.nsubdoms_xyz = [2, 5, 1]
    
    # Create simulation object
    sim = Simul(params)
    assert sim.path_run is not None


@skipif_executable_not_available("fireFoam")
def test_run_short():
    """Test running a very short fireFoam simulation"""
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/firefoam"
    params.parallel.nsubdoms = 1  # Single processor for testing
    params.controlDict.endTime = 0.01  # Very short simulation
    params.controlDict.writeInterval = 0.01
    
    sim = Simul(params)
    
    # Try to run (will only work if fireFoam is available)
    sim.make.exec("run")
    
    # Check that output exists
    assert (sim.path_run / "0").exists()
    assert (sim.path_run / "system").exists()
    assert (sim.path_run / "constant").exists()
