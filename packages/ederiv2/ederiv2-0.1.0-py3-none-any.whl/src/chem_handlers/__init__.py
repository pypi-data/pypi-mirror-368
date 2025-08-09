"""
Chemical data handling modules for eDeriv2.

This module provides tools for handling molecular data, SMILES processing,
and chemical information management.
"""

try:
    from .mol_handler import MolHandler
    from .smiles_handler import SmilesHandler, SmilesHandlingStrategyWithRDKIT
    
    __all__ = [
        "MolHandler",
        "SmilesHandler", 
        "SmilesHandlingStrategyWithRDKIT"
    ]
except ImportError as e:
    # Handle case where rdkit is not available
    __all__ = []
