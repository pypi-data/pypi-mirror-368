"""
Neuber correction is a method to correct the stress values using the Neuber correction.
"""

from neuber_correction.neuber_correction import (
    MaterialForNeuberCorrection,
    NeuberCorrection,
    NeuberSolverSettings,
)

__version__ = "0.1.5-alpha"
__all__ = ["NeuberCorrection", "MaterialForNeuberCorrection", "NeuberSolverSettings"]
