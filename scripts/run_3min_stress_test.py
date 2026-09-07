import time
import numpy as np
import json
from leanflow_antigravity import workflow

def run_3min_stress_test():
    print("Loading large-scale JHTDB dataset...")
    state, dof = workflow.load_data(subset_dof=655363)
    
    duration = 3 * 60 # 3 minutes
    start_time = time.time()
    
    print(f"Starting 3-minute performance & resiliency stress test on {dof:,} DOF...")
    cycle_idx = 1
    metrics = {
        "cycles_completed": 0,
        "total_gpu_ms": 0.0,
        "max_gauge_div": 0.0,
        "max_fp8_res": 0.0,
        "avg_speedup": 0.0,
        "errors": 0
    }
    
    while time.time() - start_time < duration:
        try:
            record = workflow.execute_cycle_step(
                state=state,
                dof=dof,
                cycle_idx=cycle_idx,
                dt=1e-3,
                nu=1e-3,
                anisotropy_ratio=1.0
            )
            
            metrics["cycles_completed"] += 1
            metrics["total_gpu_ms"] += record["gpu_ms"]
            metrics["max_gauge_div"] = max(metrics["max_gauge_div"], record["gauge_divergence"])
            metrics["max_fp8_res"] = max(metrics["max_fp8_res"], record["fp8_residual"])
            # Running average
            metrics["avg_speedup"] = metrics["avg_speedup"] + (record["speedup"] - metrics["avg_speedup"]) / metrics["cycles_completed"]
            
            cycle_idx += 1
            
            # Periodically print progress
            if cycle_idx % 500 == 0:
                elapsed = time.time() - start_time
                print(f"Elapsed: {elapsed:.1f}s | Cycles: {cycle_idx} | Speedup: {record['speedup']:.1f}x")
                
        except Exception as e:
            print(f"Error at cycle {cycle_idx}: {e}")
            metrics["errors"] += 1
            break
            
    print("\n" + "="*60)
    print(" 🚀 3-MINUTE STRESS TEST RESULTS")
    print("="*60)
    print(f"Total Cycles Completed : {metrics['cycles_completed']}")
    if metrics['cycles_completed'] > 0:
        print(f"Average GPU Latency    : {metrics['total_gpu_ms'] / metrics['cycles_completed']:.3f} ms / cycle")
    print(f"Average CPU Speedup    : {metrics['avg_speedup']:.1f}x")
    print(f"Max FP8 Residual       : {metrics['max_fp8_res']:.7f}")
    print(f"Max Gauge Divergence   : {metrics['max_gauge_div']:.4e}")
    print(f"Total Errors/Crashes   : {metrics['errors']}")
    print("="*60)
    
    with open("stress_test_3min_results.json", "w") as f:
        json.dump(metrics, f, indent=4)

if __name__ == "__main__":
    run_3min_stress_test()
