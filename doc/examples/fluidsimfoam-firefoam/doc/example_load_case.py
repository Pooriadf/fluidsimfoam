"""
Example script to load and analyze an existing fireFoam case

This demonstrates reading field data and plotting results from a completed simulation.
"""

from pathlib import Path
from fluidsimfoam.output.fields import Fields

class CaseLoader:
    """Simple wrapper to load and analyze existing OpenFOAM cases"""
    
    def __init__(self, case_path, nsubdoms=1):
        """
        Initialize case loader
        
        Parameters
        ----------
        case_path : str or Path
            Path to the OpenFOAM case directory
        nsubdoms : int
            Number of processor subdirectories (1 for serial, >1 for parallel)
        """
        self.path_run = Path(case_path)
        
        # Create minimal sim-like object for Fields class
        class SimpleParams:
            class Parallel:
                def __init__(self, nsubdoms):
                    self.nsubdoms = nsubdoms
            
            def __init__(self, nsubdoms):
                self.parallel = self.Parallel(nsubdoms)
        
        class SimpleSim:
            def __init__(self, path_run, nsubdoms):
                self.path_run = path_run
                self.params = SimpleParams(nsubdoms)
        
        class SimpleOutput:
            def __init__(self, path_run, nsubdoms):
                self.path_run = path_run
                self.sim = SimpleSim(path_run, nsubdoms)
        
        self.output = SimpleOutput(self.path_run, nsubdoms)
        self.fields = Fields(self.output)
    
    def get_times(self):
        """Get all available time directories"""
        return self.fields.get_saved_times()
    
    def read_field(self, field_name, time_approx="last"):
        """
        Read a field from the case
        
        Parameters
        ----------
        field_name : str
            Name of the field (e.g., "T", "U", "p")
        time_approx : str or float
            Time to read ("last" or specific time value)
        
        Returns
        -------
        field : Field object with .time and .get_array() method
        """
        return self.fields.read_field(field_name, time_approx)
    
    def plot_field(self, field_name, time_approx="last"):
        """Plot a field (basic implementation)"""
        return self.fields.plot_field(field_name, time_approx)
    
    def info(self):
        """Print case information"""
        print(f"Case path: {self.path_run}")
        print(f"Available times: {len(self.get_times())} time steps")
        
        # Check for common directories
        if (self.path_run / "0").exists():
            fields = list((self.path_run / "0").glob("*"))
            field_names = [f.name for f in fields if f.is_file()]
            print(f"Fields in 0/: {', '.join(field_names[:10])}")
        
        if (self.path_run / "constant").exists():
            print(f"constant/ directory exists")
        
        if (self.path_run / "system").exists():
            print(f"system/ directory exists")


def main():
    """Main function to demonstrate usage"""
    
    # Path to the existing fireFoam case
    case_path = Path("F:/Pooria/Combustion/Simulation/Geometry/for_openfoam/03dec/2")
    
    if not case_path.exists():
        print(f"Error: Case path does not exist: {case_path}")
        print("Please update the case_path to point to your OpenFOAM case")
        return
    
    # Load the case
    print("Loading fireFoam case...")
    case = CaseLoader(case_path, nsubdoms=10)  # 10 processors as shown in the original case
    
    # Display case information
    case.info()
    
    # Get available times
    times = case.get_times()
    print(f"\nTime range: {times[0]:.3f} to {times[-1]:.3f}")
    print(f"Available times: {times}")
    
    # Read some fields
    print("\n" + "="*60)
    print("Reading fields from last time step...")
    print("="*60)
    
    try:
        # Temperature field
        print("\n1. Temperature (T):")
        T = case.read_field("T", time_approx="last")
        T_array = T.get_array()
        print(f"   Time: {T.time}")
        print(f"   Min: {T_array.min():.2f} K")
        print(f"   Max: {T_array.max():.2f} K")
        print(f"   Mean: {T_array.mean():.2f} K")
    except Exception as e:
        print(f"   Error reading T: {e}")
    
    try:
        # Velocity field
        print("\n2. Velocity (U):")
        U = case.read_field("U", time_approx="last")
        U_array = U.get_array()
        print(f"   Time: {U.time}")
        print(f"   Shape: {U_array.shape}")
        if len(U_array.shape) > 1:
            # Vector field
            U_mag = (U_array**2).sum(axis=1)**0.5
            print(f"   Magnitude - Min: {U_mag.min():.3f} m/s, Max: {U_mag.max():.3f} m/s")
        else:
            print(f"   Min: {U_array.min():.3f} m/s")
            print(f"   Max: {U_array.max():.3f} m/s")
    except Exception as e:
        print(f"   Error reading U: {e}")
    
    try:
        # Oxygen concentration
        print("\n3. Oxygen (O2):")
        O2 = case.read_field("O2", time_approx="last")
        O2_array = O2.get_array()
        print(f"   Time: {O2.time}")
        print(f"   Min: {O2_array.min():.4f}")
        print(f"   Max: {O2_array.max():.4f}")
        print(f"   Mean: {O2_array.mean():.4f}")
    except Exception as e:
        print(f"   Error reading O2: {e}")
    
    try:
        # Fuel concentration
        print("\n4. Fuel (C7H16):")
        fuel = case.read_field("C7H16", time_approx="last")
        fuel_array = fuel.get_array()
        print(f"   Time: {fuel.time}")
        print(f"   Min: {fuel_array.min():.6f}")
        print(f"   Max: {fuel_array.max():.6f}")
        print(f"   Mean: {fuel_array.mean():.6f}")
    except Exception as e:
        print(f"   Error reading C7H16: {e}")
    
    print("\n" + "="*60)
    print("To create plots, you can use:")
    print("  case.plot_field('T', time_approx='last')")
    print("  case.fields.plot_contour(variable='T', mesh_opacity=0.1)")
    print("  case.fields.plot_boundary(name='inlet', color='r')")
    print("="*60)


if __name__ == "__main__":
    main()
