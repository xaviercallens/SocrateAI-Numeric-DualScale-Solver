"""
LeanFlow AI Module — Neuro-Symbolic AI Preprocessing & Preconditioning
======================================================================
Provides AI-driven mesh generation, boundary condition inference,
parameter tuning, and SymBrain adaptive routing for Navier–Stokes PDEs.
"""

from .preprocessing import (
    NeuroSymbolicMesher,
    BoundaryConditionInference,
    ParameterTuner,
    ZeroShotFluidSurrogate,
    AIPreprocessingResult,
    run_ai_preprocessing_pipeline,
)

__all__ = [
    "NeuroSymbolicMesher",
    "BoundaryConditionInference",
    "ParameterTuner",
    "ZeroShotFluidSurrogate",
    "AIPreprocessingResult",
    "run_ai_preprocessing_pipeline",
]
