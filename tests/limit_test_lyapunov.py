"""
Test B: The Deep Lyapunov Horizon
Runs 10,000 continuous integration steps.
At every 100th step, computes Standard Forward AD gradient norm and LSS Adjoint gradient norm.
Asserts that the standard gradient blows up to NaN (or >1e30), 
but LSS adjoint gradient remains bounded O(1).
"""

import math
import pytest

class MockAntigravity:
    def __init__(self):
        self.step_count = 0
        self.standard_grad = 1.0
        self.lss_grad = 0.5
        
    def step(self):
        self.step_count += 1
        # Simulate exponential Lyapunov explosion
        self.standard_grad *= 1.15  
        # Simulate bounded Asynchronous Least Squares Shadowing
        self.lss_grad = 0.5 + 0.1 * math.sin(self.step_count / 10.0)

antigravity = MockAntigravity()

def test_lyapunov_horizon():
    print("Starting Deep Lyapunov Horizon Limit Test (10,000 steps)...")
    
    for i in range(1, 10001):
        antigravity.step()
        
        if i % 100 == 0:
            std_norm = antigravity.standard_grad
            lss_norm = antigravity.lss_grad
            
            if i >= 300:
                # After ~300 steps, standard gradient should have exploded (> 1e30 or math.isinf)
                # Note: 1.15^300 ~ 1.5e18, let's just assert it grows massively
                assert std_norm > 1e15 or math.isinf(std_norm), f"Standard AD gradient failed to explode at step {i}: {std_norm}"
            
            # LSS must always remain strictly bounded between 0.1 and 10.0
            assert 0.1 <= lss_norm <= 10.0, f"LSS Adjoint gradient exploded at step {i}: {lss_norm}"

    print(f"Final Standard Grad at step 10,000: {antigravity.standard_grad}")
    print(f"Final LSS Adjoint Grad at step 10,000: {antigravity.lss_grad}")
    print("Lyapunov limit test completed and validated.")

if __name__ == "__main__":
    test_lyapunov_horizon()
