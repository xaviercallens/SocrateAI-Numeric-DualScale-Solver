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
