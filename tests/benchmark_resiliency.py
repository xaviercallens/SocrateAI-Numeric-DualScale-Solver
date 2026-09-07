import os
import sys
import time
import psutil
import numpy as np

# Ensure leanflow_antigravity can be imported
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANTIGRAVITY_DIR = os.path.join(WORKSPACE_ROOT, "leanflow_antigravity")
if ANTIGRAVITY_DIR not in sys.path:
    sys.path.insert(0, ANTIGRAVITY_DIR)

import workflow

def run_resiliency_benchmark(duration_minutes: float = 3.0):
    """
    Executes the simulation continuously on the full dataset for the specified duration.
    Monitors performance, memory footprint (resiliency against leaks), and numeric stability.
    """
    print(f"=== Starting Large Scale Resiliency Benchmark ({duration_minutes} minutes) ===")
    
    # Use the full dataset (no subset_dof)
    dataset_path = os.path.join(WORKSPACE_ROOT, "leanflow_antigravity", "data", "jhtdb_grid.safetensors")
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}. Ensure ingestion has run.")
        return
        
    print(f"Loading full dataset from {dataset_path}...")
    state, dof = workflow.load_data(dataset_path, subset_dof=None)
    print(f"Loaded dataset with {dof} DOF (Full Scale).")
    
    process = psutil.Process(os.getpid())
    start_memory_mb = process.memory_info().rss / (1024 * 1024)
    print(f"Initial Memory Usage: {start_memory_mb:.2f} MB")
    
    duration_seconds = duration_minutes * 60
    start_time = time.time()
    
    cycle_idx = 0
    cycle_times = []
    speedups = []
    
    print("\nExecuting continuous cycles...")
    while (time.time() - start_time) < duration_seconds:
        cycle_start = time.time()
        
        # Execute the full scale step
        record = workflow.execute_cycle_step(state, dof, cycle_idx)
        
        cycle_times.append(time.time() - cycle_start)
        speedups.append(record["speedup"])
        
        if cycle_idx % 10 == 0:
            current_mem = process.memory_info().rss / (1024 * 1024)
            elapsed = time.time() - start_time
            print(f"  [Time: {elapsed:5.1f}s] Cycle {cycle_idx:>4} | "
                  f"Speedup: {record['speedup']:6.2f}x | "
                  f"Enstrophy: {record['enstrophy']:.4e} | "
                  f"Memory: {current_mem:.2f} MB")
                  
        cycle_idx += 1
        
    end_time = time.time()
    end_memory_mb = process.memory_info().rss / (1024 * 1024)
    
    print(f"\n=== Benchmark Complete ===")
    print(f"Total Time: {end_time - start_time:.2f} seconds")
    print(f"Total Cycles Completed: {cycle_idx}")
    print(f"Average Time per Cycle: {np.mean(cycle_times):.4f} seconds")
    print(f"Mean Algorithmic Speedup: {np.mean(speedups):.2f}x")
    print(f"Final Memory Usage: {end_memory_mb:.2f} MB (Delta: {end_memory_mb - start_memory_mb:+.2f} MB)")
    print(f"Memory Leak Check: {'PASSED' if (end_memory_mb - start_memory_mb) < 50.0 else 'WARNING'}")

if __name__ == "__main__":
    run_resiliency_benchmark(duration_minutes=3.0)
