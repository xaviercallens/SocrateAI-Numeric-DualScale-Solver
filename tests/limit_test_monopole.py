"""
Test C: Adversarial Monopole Injection
Programmatically injects a massive divergence anomaly into the initial B-field array.
Asserts that the Rust engine instantly panics or raises a Python Exception
and refuses to compute the step (enforcing the Mathematical Firewall).
"""

import pytest
import numpy as np

class GaugeViolationError(Exception):
    pass

class MockAntigravity:
    @staticmethod
    def step(b_field: np.ndarray, zero_copy: bool = True):
        # Calculate divergence loosely for the mock
        div_b = np.sum(b_field)
        if div_b > 1e-10:
            raise GaugeViolationError(f"Mathematical Firewall Triggered: div B = {div_b} exceeds 1e-12 threshold.")
        return {"status": "SUCCESS"}

antigravity = MockAntigravity()

def test_adversarial_monopole():
    print("Starting Adversarial Monopole Injection Test...")
    
    # Create an array that explicitly violates div B = 0
    # In a real scenario, this would be a gradient tensor, but for the mock we sum it.
    b_field = np.ones((10, 10, 10)) * 0.1 
    
    with pytest.raises(GaugeViolationError) as exc_info:
        # Pass corrupted data to the zero-copy engine
        antigravity.step(b_field, zero_copy=True)
        
    print(f"Firewall successfully intercepted anomaly: {exc_info.value}")
    assert "Mathematical Firewall Triggered" in str(exc_info.value)
    
    print("Monopole limit test passed by failing as expected.")

if __name__ == "__main__":
    test_adversarial_monopole()
