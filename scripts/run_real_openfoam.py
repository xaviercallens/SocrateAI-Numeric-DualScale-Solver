import sys
import os
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from run_jhtdb_openfoam_real_comparison import fetch_jhtdb_velocity_cutout

# Import the functions we just wrote
import run_openfoam_jhtdb_binary as of_wrapper

if __name__ == "__main__":
    print("Setting up OpenFOAM case with JHTDB real data...")
    jhtdb_res = fetch_jhtdb_velocity_cutout(output_path="/tmp/jhtdb_cache", n=32)
    jhtdb_vel = jhtdb_res["velocity"]
    
    case_dir = "/tmp/jhtdb_openfoam"
    if os.path.exists(case_dir):
        shutil.rmtree(case_dir)
        
    of_wrapper.generate_openfoam_case(case_dir, jhtdb_vel[0], jhtdb_vel[1], n_grid=32, nu=1e-3, dt=5e-4, n_steps=200)
    res = of_wrapper.run_openfoam(case_dir)
    print("--- OpenFOAM Binary Results ---")
    print(res)
