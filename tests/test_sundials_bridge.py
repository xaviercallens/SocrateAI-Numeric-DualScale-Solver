"""
Unit tests for the rusty-SUNDIALS bridge.
"""

from dualscale_solver.runtimes.sundials_bridge import RustySundialsBridge


def test_rusty_sundials_detection():
    bridge = RustySundialsBridge()
    report = bridge.probe()
    assert report.available is True
    assert report.crates["cvode"] is True
    assert report.crates["nvector"] is True
    assert "bdf_orders" in report.methods
    assert report.nvector_backends["SerialVector"] is True

def test_native_cvode_integrate():
    from dualscale_solver.runtimes.sundials_bridge import native_cvode_integrate
    import numpy as np
    
    n_shells = 10
    u0 = np.zeros(n_shells, dtype=np.float64)
    u0[0] = 1.0
    u0[1] = 0.5
    
    res = native_cvode_integrate(
        n_shells=n_shells,
        nu=1e-3,
        alpha_prime=0.01,
        use_bdf=True,
        rtol=1e-4,
        atol=1e-6,
        u0=u0,
        t_final=0.05,
        n_steps=5
    )
    
    assert res["num_steps"] > 0
    assert len(res["times"]) == 6
    assert len(res["energy"]) == 6
    assert res["energy"][-1] <= res["energy"][0]
    assert len(res["final_state"]) == n_shells
