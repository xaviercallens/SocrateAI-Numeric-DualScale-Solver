#!/usr/bin/env python3
"""
src/dualscale_solver/benchmarks/usecase_database.py

LeanFlow Enterprise — Reference Use Case Database
====================================================

Central registry of 5 canonical PDE benchmark use cases (UC7–UC11) with:
  - Dataset download metadata (Hugging Face, Zenodo, GitHub)
  - Reference solver results from published DNS / analytical solutions
  - Acceptance criteria for automated validation gates
  - LeanFlow simulation parameters

References:
  [1] Takamoto et al. (2022) PDEBench. NeurIPS 2022. arXiv:2210.07182
  [2] Ghia, Ghia & Shin (1982) J. Comp. Phys. 48(3):387–411
  [3] Burns et al. (2020) Dedalus. Phys. Rev. Research 2:023068
  [4] Stone et al. (2020) Athena++. ApJS 249:4
  [5] Li et al. (2008) JHTDB. J. Turbulence 9(31):1–29
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class DatasetSource(str, Enum):
    HUGGINGFACE = "huggingface"
    ZENODO = "zenodo"
    GITHUB = "github"
    LOCAL = "local"


class UseCaseStatus(str, Enum):
    PROPOSED = "PROPOSED"
    IMPLEMENTED = "IMPLEMENTED"
    VALIDATED = "VALIDATED"
    CERTIFIED = "CERTIFIED"


# ---------------------------------------------------------------------------
# Dataset Descriptor
# ---------------------------------------------------------------------------

@dataclass
class DatasetDescriptor:
    """Describes a downloadable reference dataset."""
    source: DatasetSource
    name: str
    doi: str = ""
    url: str = ""
    repo_id: str = ""
    filename: str = ""
    repo_type: str = "dataset"
    format: str = "HDF5"
    size_gb: float = 0.0
    citation: str = ""
    note: str = ""


# ---------------------------------------------------------------------------
# Reference Result
# ---------------------------------------------------------------------------

@dataclass
class ReferenceResult:
    """A single quantitative reference result from a published source."""
    metric: str
    value: float
    unit: str = ""
    tolerance: float = 0.0
    source: str = ""
    note: str = ""


# ---------------------------------------------------------------------------
# Acceptance Criterion
# ---------------------------------------------------------------------------

@dataclass
class AcceptanceCriterion:
    """Quantitative pass/fail criterion for a use case."""
    metric: str
    threshold: float
    comparator: str = "<"  # "<", ">", "<=", ">=", "within"
    unit: str = ""
    description: str = ""

    def evaluate(self, measured: float) -> bool:
        """Evaluate whether the measured value passes this criterion."""
        if self.comparator == "<":
            return measured < self.threshold
        elif self.comparator == "<=":
            return measured <= self.threshold
        elif self.comparator == ">":
            return measured > self.threshold
        elif self.comparator == ">=":
            return measured >= self.threshold
        elif self.comparator == "within":
            return abs(measured) <= self.threshold
        return False


# ---------------------------------------------------------------------------
# Use Case Definition
# ---------------------------------------------------------------------------

@dataclass
class UseCaseDefinition:
    """Complete definition of a reference benchmark use case."""
    id: str
    name: str
    description: str
    physics: str
    reference_solver: str
    governing_equations: str
    datasets: List[DatasetDescriptor] = field(default_factory=list)
    simulation_params: Dict[str, Any] = field(default_factory=dict)
    reference_results: List[ReferenceResult] = field(default_factory=list)
    acceptance_criteria: List[AcceptanceCriterion] = field(default_factory=list)
    status: UseCaseStatus = UseCaseStatus.PROPOSED
    leanflow_module: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        for ds in d["datasets"]:
            ds["source"] = ds["source"].value if isinstance(ds["source"], DatasetSource) else ds["source"]
        return d


# ---------------------------------------------------------------------------
# Ghia et al. (1982) Reference Tables — Lid-Driven Cavity
# ---------------------------------------------------------------------------

GHIA_REFERENCE = {
    100: {
        "y": [0.0000, 0.0547, 0.0625, 0.0703, 0.1016, 0.1719, 0.2813,
              0.4531, 0.5000, 0.6172, 0.7344, 0.8516, 0.9531, 0.9609,
              0.9688, 0.9766, 1.0000],
        "u": [0.0000, -0.03717, -0.04192, -0.04775, -0.06434, -0.10150,
              -0.15662, -0.21090, -0.20581, -0.13641, 0.00332, 0.23151,
              0.68717, 0.73722, 0.78871, 0.84123, 1.00000],
    },
    400: {
        "y": [0.0000, 0.0547, 0.0625, 0.0703, 0.1016, 0.1719, 0.2813,
              0.4531, 0.5000, 0.6172, 0.7344, 0.8516, 0.9531, 0.9609,
              0.9688, 0.9766, 1.0000],
        "u": [0.0000, -0.08186, -0.09266, -0.10338, -0.14612, -0.24299,
              -0.32726, -0.17119, -0.11477, 0.02135, 0.16256, 0.29093,
              0.55892, 0.61756, 0.68439, 0.75837, 1.00000],
    },
    1000: {
        "y": [0.0000, 0.0547, 0.0625, 0.0703, 0.1016, 0.1719, 0.2813,
              0.4531, 0.5000, 0.6172, 0.7344, 0.8516, 0.9531, 0.9609,
              0.9688, 0.9766, 1.0000],
        "u": [0.0000, -0.18109, -0.20196, -0.22220, -0.29730, -0.38289,
              -0.27805, -0.10648, -0.06080, 0.05702, 0.18719, 0.33304,
              0.46604, 0.51117, 0.57492, 0.65928, 1.00000],
    },
    3200: {
        "y": [0.0000, 0.0547, 0.0625, 0.0703, 0.1016, 0.1719, 0.2813,
              0.4531, 0.5000, 0.6172, 0.7344, 0.8516, 0.9531, 0.9609,
              0.9688, 0.9766, 1.0000],
        "u": [0.0000, -0.32407, -0.35344, -0.37827, -0.41933, -0.34323,
              -0.24427, -0.86636, -0.04272, 0.07156, 0.19791, 0.34682,
              0.46101, 0.46547, 0.48296, 0.53236, 1.00000],
    },
    5000: {
        "y": [0.0000, 0.0547, 0.0625, 0.0703, 0.1016, 0.1719, 0.2813,
              0.4531, 0.5000, 0.6172, 0.7344, 0.8516, 0.9531, 0.9609,
              0.9688, 0.9766, 1.0000],
        "u": [0.0000, -0.41165, -0.42901, -0.43643, -0.40435, -0.33050,
              -0.22855, -0.07404, -0.03039, 0.08183, 0.20087, 0.33556,
              0.46036, 0.45992, 0.46120, 0.48223, 1.00000],
    },
    10000: {
        "y": [0.0000, 0.0547, 0.0625, 0.0703, 0.1016, 0.1719, 0.2813,
              0.4531, 0.5000, 0.6172, 0.7344, 0.8516, 0.9531, 0.9609,
              0.9688, 0.9766, 1.0000],
        "u": [0.0000, -0.42735, -0.42537, -0.41657, -0.38000, -0.32709,
              -0.23186, -0.07540, -0.03111, 0.08344, 0.20673, 0.34635,
              0.47133, 0.47505, 0.47804, 0.49187, 1.00000],
    },
}

# Primary vortex center locations from Ghia (1982) and Botella & Peyret (1998)
GHIA_VORTEX_CENTERS = {
    100:   {"x": 0.6172, "y": 0.7344},
    400:   {"x": 0.5547, "y": 0.6055},
    1000:  {"x": 0.5313, "y": 0.5625},
    3200:  {"x": 0.5165, "y": 0.5469},
    5000:  {"x": 0.5117, "y": 0.5352},
    10000: {"x": 0.5117, "y": 0.5303},
}


# ---------------------------------------------------------------------------
# JHTDB Reference Parameters
# ---------------------------------------------------------------------------

JHTDB_ISOTROPIC_PARAMS = {
    "re_lambda": 433.0,
    "nu": 1.85e-4,
    "epsilon": 0.103,
    "eta": 2.87e-3,       # Kolmogorov scale
    "L_integral": 1.36,   # integral length scale
    "lambda_taylor": 0.113,  # Taylor micro-scale
    "u_rms": 0.681,       # RMS velocity
    "dns_grid": 1024,
    "spectral_slope": -5.0 / 3.0,
}


# ---------------------------------------------------------------------------
# Use Case Factory
# ---------------------------------------------------------------------------

def build_uc7_taylor_green() -> UseCaseDefinition:
    """UC7: 2D Taylor-Green Vortex Decay — PDEBench validation."""
    return UseCaseDefinition(
        id="UC7",
        name="Taylor-Green Vortex 2D Decay",
        description=(
            "Canonical incompressible NS benchmark with exact analytical solution. "
            "Validates spectral accuracy, energy decay rate, and solenoidal preservation."
        ),
        physics="2D incompressible Navier-Stokes, periodic box",
        reference_solver="PDEBench pseudo-spectral DNS (Takamoto et al. 2022)",
        governing_equations="du/dt + (u·∇)u = -∇p + ν∇²u, ∇·u = 0",
        leanflow_module="PseudoSpectralNavierStokes2D",
        datasets=[
            DatasetDescriptor(
                source=DatasetSource.HUGGINGFACE,
                name="PDEBench NavierStokes-2D",
                repo_id="pdearena/NavierStokes-2D",
                filename="NavierStokes-2D_test.h5",
                doi="10.48550/arXiv.2210.07182",
                format="HDF5",
                size_gb=2.0,
                citation="Takamoto et al. (2022) PDEBench. NeurIPS 2022.",
            ),
            DatasetDescriptor(
                source=DatasetSource.ZENODO,
                name="PDEBench Raw Data",
                url="https://zenodo.org/records/5957056",
                doi="10.5281/zenodo.5957056",
                format="HDF5",
                size_gb=2.0,
            ),
        ],
        simulation_params={
            "grid": 128,
            "domain": "[0, 2π)²",
            "nu": 1e-3,
            "alpha_prime": 0.01,
            "integrator": "CVODE BDF",
            "dt": "adaptive (CFL ≤ 0.5)",
            "t_final": 10.0,
            "projection": "Leray-Helmholtz",
            "dealiasing": "Orszag 2/3 rule",
        },
        reference_results=[
            ReferenceResult("energy_decay_analytical", 0.0, unit="",
                            source="Exact: E(t) = E₀·exp(-4νt)"),
            ReferenceResult("L2_error_spectral_t1", 1e-6, unit="",
                            source="PDEBench spectral reference"),
            ReferenceResult("L2_error_fvm_t1", 1e-4, unit="",
                            source="2nd-order FVM baseline"),
            ReferenceResult("rk4_steps_cfl", 1e5, unit="steps",
                            source="CFL-limited explicit RK4"),
        ],
        acceptance_criteria=[
            AcceptanceCriterion("L2_error_t1", 1e-8, "<", "",
                                "L² error vs analytical at t=1"),
            AcceptanceCriterion("energy_relative_error", 1e-10, "<", "",
                                "|E_LF(t) - E_exact(t)| / E₀"),
            AcceptanceCriterion("solenoidal_residual", 1e-12, "<", "",
                                "‖∇·u‖∞ machine-precision solenoidal"),
            AcceptanceCriterion("cvode_steps", 2000, "<", "steps",
                                "BDF steps ≪ 10⁵ RK4 steps"),
        ],
    )


def build_uc8_lid_driven_cavity() -> UseCaseDefinition:
    """UC8: 2D Lid-Driven Cavity — Ghia et al. (1982) benchmark."""
    return UseCaseDefinition(
        id="UC8",
        name="2D Lid-Driven Cavity Flow",
        description=(
            "Gold-standard CFD benchmark. Square cavity with moving top wall. "
            "Validates steady-state convergence, vortex center tracking, "
            "and centerline velocity profiles against Ghia (1982)."
        ),
        physics="2D incompressible NS in enclosed cavity",
        reference_solver="Ghia, Ghia & Shin (1982) multigrid; Botella & Peyret (1998) Chebyshev",
        governing_equations="du/dt + (u·∇)u = -∇p + ν∇²u, ∇·u = 0, u|_wall = BC",
        leanflow_module="PseudoSpectralNavierStokes2D + IDA DAE + volume penalization",
        datasets=[
            DatasetDescriptor(
                source=DatasetSource.ZENODO,
                name="CFDBench",
                url="https://zenodo.org/records/7813803",
                doi="10.5281/zenodo.7813803",
                format="CSV/NPZ",
                size_gb=0.5,
                citation="Luo et al. (2023) CFDBench. arXiv:2310.05963",
                note="Includes Ghia reference tables as validation data",
            ),
            DatasetDescriptor(
                source=DatasetSource.GITHUB,
                name="Ghia Reference Tables (embedded in code)",
                url="https://github.com/Shengfeng233/PINN-for-NS-equation",
                format="Python arrays",
                note="Ghia 1982 data digitized as Python arrays",
            ),
        ],
        simulation_params={
            "grid": 128,
            "domain": "[0,1]²",
            "re_sweep": [100, 400, 1000, 3200, 5000, 10000],
            "bc_top": "u=1, v=0",
            "bc_walls": "no-slip (volume penalization, η=1e-4)",
            "integrator": "IDA DAE solenoidal",
            "steady_state_tol": 1e-8,
            "alpha_prime": 0.01,
        },
        reference_results=[
            ReferenceResult("ghia_centerline_u_re100", 0.0, unit="",
                            source="Ghia (1982) Table I"),
            ReferenceResult("ghia_centerline_u_re1000", 0.0, unit="",
                            source="Ghia (1982) Table I"),
            ReferenceResult("vortex_center_re1000_x", 0.5313, unit="",
                            source="Ghia (1982)"),
            ReferenceResult("vortex_center_re1000_y", 0.5625, unit="",
                            source="Ghia (1982)"),
        ],
        acceptance_criteria=[
            AcceptanceCriterion("centerline_u_linf_error", 0.005, "<", "",
                                "‖u_LF - u_Ghia‖∞ on vertical centerline"),
            AcceptanceCriterion("vortex_center_error_cells", 1.0, "<=", "grid cells",
                                "Primary vortex center within 1 cell of Ghia"),
            AcceptanceCriterion("divergence_residual", 1e-10, "<", "",
                                "Solenoidal residual at steady state"),
            AcceptanceCriterion("ida_steps_to_steady", 1e4, "<", "steps",
                                "IDA DAE steps ≪ 10⁶ explicit"),
        ],
    )


def build_uc9_rayleigh_benard() -> UseCaseDefinition:
    """UC9: 2D Rayleigh-Bénard Convection — Dedalus validation."""
    return UseCaseDefinition(
        id="UC9",
        name="2D Rayleigh-Bénard Convection",
        description=(
            "Buoyancy-driven convection between hot bottom and cold top plate. "
            "Validates Nusselt number scaling Nu ~ Ra^0.29 and thermal "
            "boundary layer resolution."
        ),
        physics="2D Boussinesq Navier-Stokes with buoyancy",
        reference_solver="Dedalus spectral (Burns et al. 2020); Johnston & Doering (2009)",
        governing_equations=(
            "du/dt + (u·∇)u = -∇p + Pr·∇²u + Ra·Pr·T·ê_y, "
            "dT/dt + (u·∇)T = ∇²T, ∇·u = 0"
        ),
        leanflow_module="PseudoSpectralNavierStokes2D + Boussinesq buoyancy",
        datasets=[
            DatasetDescriptor(
                source=DatasetSource.ZENODO,
                name="Dedalus RB Convection Data",
                url="https://zenodo.org/records/5520633",
                doi="10.5281/zenodo.5520633",
                format="HDF5",
                size_gb=1.5,
                citation="Burns et al. (2020) Dedalus.",
            ),
            DatasetDescriptor(
                source=DatasetSource.GITHUB,
                name="Dedalus RB Example",
                url="https://github.com/DedalusProject/dedalus",
                format="Python scripts",
                note="examples/ivp_2d_rayleigh_benard",
            ),
        ],
        simulation_params={
            "grid": "256×128",
            "domain": "[0, 2π) × [0, 1]",
            "ra": 1e6,
            "pr": 1.0,
            "bc_y": "no-slip walls, T_bot=1, T_top=0",
            "bc_x": "periodic",
            "integrator": "CVODE BDF",
            "t_final": 200.0,
            "alpha_prime": 0.05,
        },
        reference_results=[
            ReferenceResult("nusselt_number_ra1e6", 8.92, unit="",
                            tolerance=0.05,
                            source="Johnston & Doering (2009)"),
            ReferenceResult("nu_scaling_exponent", 0.29, unit="",
                            tolerance=0.01,
                            source="Grossmann-Lohse theory"),
            ReferenceResult("re_rms", 1200.0, unit="",
                            source="Dedalus DNS"),
        ],
        acceptance_criteria=[
            AcceptanceCriterion("nusselt_error", 0.3, "<", "",
                                "|Nu_LF - 8.92| < 0.3 (< 3%)"),
            AcceptanceCriterion("nu_scaling_exponent", 0.31, "<=", "",
                                "β ∈ [0.27, 0.31]"),
            AcceptanceCriterion("solenoidal_residual", 1e-10, "<", "",
                                "Leray + IDA DAE"),
        ],
    )


def build_uc10_kelvin_helmholtz() -> UseCaseDefinition:
    """UC10: 2D Kelvin-Helmholtz Instability — Athena++ validation."""
    return UseCaseDefinition(
        id="UC10",
        name="2D Kelvin-Helmholtz Instability",
        description=(
            "Shear instability benchmark testing advection accuracy and "
            "numerical diffusion. Validates roll-up timing, vortex pairing, "
            "and kinetic energy conservation."
        ),
        physics="2D incompressible shear flow instability",
        reference_solver="Athena++ (Stone et al. 2020); Lecoanet et al. (2016) spectral DNS",
        governing_equations="du/dt + (u·∇)u = -∇p + ν∇²u, ∇·u = 0",
        leanflow_module="PseudoSpectralNavierStokes2D",
        datasets=[
            DatasetDescriptor(
                source=DatasetSource.GITHUB,
                name="Athena++ KH Test Problem",
                url="https://github.com/PrincetonUniversity/athena",
                format="VTK/HDF5",
                citation="Stone et al. (2020) ApJS 249:4",
                note="src/pgen/kh.cpp reference implementation",
            ),
            DatasetDescriptor(
                source=DatasetSource.HUGGINGFACE,
                name="PDEBench NavierStokes-2D (turbulent superset)",
                repo_id="pdearena/NavierStokes-2D",
                format="HDF5",
                doi="10.48550/arXiv.2210.07182",
            ),
        ],
        simulation_params={
            "grid": 256,
            "domain": "[0, 1)²",
            "u0": 1.0,
            "delta": 0.02,
            "perturbation_amp": 0.01,
            "nu": 1e-4,
            "alpha_prime": 0.05,
            "integrator": "CVODE BDF",
            "t_final": 4.0,
            "dealiasing": "Orszag 2/3 rule",
        },
        reference_results=[
            ReferenceResult("rollup_time", 0.65, unit="s",
                            tolerance=0.05,
                            source="Linear stability: σ ≈ k·U₀/2"),
            ReferenceResult("vortex_pairing_time", 2.0, unit="s",
                            source="Athena++ / Lecoanet (2016)"),
            ReferenceResult("enstrophy_peak_time", 1.0, unit="s",
                            source="Spectral DNS reference"),
            ReferenceResult("mixing_width_slope", 0.1, unit="",
                            tolerance=0.02,
                            source="Self-similar theory"),
        ],
        acceptance_criteria=[
            AcceptanceCriterion("rollup_timing_error_pct", 5.0, "<", "%",
                                "Roll-up timing within 5% of reference"),
            AcceptanceCriterion("energy_conservation_inviscid", 1e-8, "<", "",
                                "|E(t)-E(0)|/E(0) in inviscid limit"),
            AcceptanceCriterion("mixing_width_slope", 0.12, "<=", "",
                                "h'(t) ∈ [0.08, 0.12] post-saturation"),
            AcceptanceCriterion("cvode_steps", 5000, "<", "steps",
                                "BDF steps ≪ 5×10⁵ explicit"),
        ],
    )


def build_uc11_jhtdb_isotropic() -> UseCaseDefinition:
    """UC11: 3D Forced Isotropic Turbulence — JHTDB DNS validation."""
    return UseCaseDefinition(
        id="UC11",
        name="3D Forced Isotropic Turbulence (JHTDB)",
        description=(
            "Statistically stationary HIT benchmark at Re_λ≈433. "
            "Validates Kolmogorov -5/3 spectral slope, dissipation rate, "
            "and energy cascade dynamics."
        ),
        physics="3D incompressible HIT with large-scale forcing",
        reference_solver="JHTDB pseudo-spectral DNS 1024³ (Li et al. 2008)",
        governing_equations="du/dt + (u·∇)u = -∇p + ν∇²u + f, ∇·u = 0",
        leanflow_module="DyadicShellSolver + PseudoSpectralNavierStokes3D",
        datasets=[
            DatasetDescriptor(
                source=DatasetSource.HUGGINGFACE,
                name="LeanFlow Phase12 Benchmark (JHTDB subset)",
                repo_id="callensxavier/leanflow-phase12-benchmark",
                filename="jhtdb_isotropic_64cube.h5",
                doi="10.1080/14685240802376389",
                format="HDF5",
                size_gb=0.3,
                citation="Li et al. (2008) J. Turbulence 9(31):1–29",
            ),
            DatasetDescriptor(
                source=DatasetSource.LOCAL,
                name="JHTDB REST API",
                url="http://turbulence.pha.jhu.edu",
                note="pip install pyJHTDB for direct 1024³ access",
            ),
        ],
        simulation_params={
            "grid": 64,
            "domain": "[0, 2π)³",
            "nu": 1.85e-4,
            "forcing_shells": "k ∈ [1, 2]",
            "epsilon_in": 0.103,
            "alpha_prime": 0.1,
            "integrator": "CVODE BDF",
            "t_final": "5 large-eddy turnovers",
            "projection": "3D Leray-Helmholtz",
        },
        reference_results=[
            ReferenceResult("re_lambda", 433.0, unit="",
                            source="JHTDB DNS"),
            ReferenceResult("kolmogorov_eta", 2.87e-3, unit="m",
                            source="η = (ν³/ε)^(1/4)"),
            ReferenceResult("dissipation_rate", 0.103, unit="",
                            source="JHTDB measured"),
            ReferenceResult("spectral_slope", -5.0 / 3.0, unit="",
                            tolerance=0.05,
                            source="Kolmogorov (1941)"),
            ReferenceResult("integral_length", 1.36, unit="m",
                            source="JHTDB computed"),
        ],
        acceptance_criteria=[
            AcceptanceCriterion("spectral_slope_error", 0.15, "<", "",
                                "|-5/3 - measured_slope| < 0.15"),
            AcceptanceCriterion("dissipation_rate_error_pct", 15.0, "<", "%",
                                "|ε_LF - 0.103| / 0.103 < 15%"),
            AcceptanceCriterion("energy_conservation_per_turnover", 0.001, "<", "",
                                "|ΔE/E| < 0.1% per turnover"),
            AcceptanceCriterion("kolmogorov_exponent", -1.5, "<=", "",
                                "Exponent ∈ [-1.8, -1.5]"),
        ],
    )


# ---------------------------------------------------------------------------
# Global Registry
# ---------------------------------------------------------------------------

def build_usecase_registry() -> Dict[str, UseCaseDefinition]:
    """Build the complete registry of all 5 reference use cases."""
    return {
        "UC7": build_uc7_taylor_green(),
        "UC8": build_uc8_lid_driven_cavity(),
        "UC9": build_uc9_rayleigh_benard(),
        "UC10": build_uc10_kelvin_helmholtz(),
        "UC11": build_uc11_jhtdb_isotropic(),
    }


def export_registry_json(output_path: Path) -> None:
    """Export the full use case registry to a JSON file."""
    registry = build_usecase_registry()
    data = {k: v.to_dict() for k, v in registry.items()}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ---------------------------------------------------------------------------
# Dataset Download Registry (flat dict for scripting)
# ---------------------------------------------------------------------------

DATASET_DOWNLOAD_REGISTRY = {
    "UC7_taylor_green_pdebench": {
        "source": "huggingface",
        "repo_id": "pdearena/NavierStokes-2D",
        "filename": "NavierStokes-2D_test.h5",
        "repo_type": "dataset",
        "doi": "10.48550/arXiv.2210.07182",
        "size_gb": 2.0,
        "format": "HDF5",
    },
    "UC8_lid_driven_cavity_ghia": {
        "source": "zenodo",
        "zenodo_id": "7813803",
        "url": "https://zenodo.org/records/7813803",
        "doi": "10.5281/zenodo.7813803",
        "size_gb": 0.5,
        "format": "CSV/NPZ",
        "note": "CFDBench dataset, includes Ghia et al. reference tables",
    },
    "UC9_rayleigh_benard_dedalus": {
        "source": "zenodo",
        "zenodo_id": "5520633",
        "url": "https://zenodo.org/records/5520633",
        "doi": "10.5281/zenodo.5520633",
        "size_gb": 1.5,
        "format": "HDF5",
        "note": "Dedalus 2D RB convection snapshots",
    },
    "UC10_kelvin_helmholtz_athena": {
        "source": "github",
        "repo": "PrincetonUniversity/athena",
        "url": "https://github.com/PrincetonUniversity/athena",
        "reference": "Stone et al. 2020, ApJS 249:4",
        "format": "VTK/HDF5",
        "note": "KH test problem input deck + reference solution",
    },
    "UC11_jhtdb_isotropic_turbulence": {
        "source": "huggingface",
        "repo_id": "callensxavier/leanflow-phase12-benchmark",
        "filename": "jhtdb_isotropic_64cube.h5",
        "repo_type": "dataset",
        "doi": "10.1080/14685240802376389",
        "api_url": "http://turbulence.pha.jhu.edu",
        "size_gb": 0.3,
        "format": "HDF5",
    },
}
