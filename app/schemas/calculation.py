"""Compatibility shim for singular module import.

Some tests and older code import `app.schemas.calculation` (singular).
The canonical module is `calculations.py`; provide a thin shim
to avoid breaking imports.
"""
from .calculations import (
    CalculationType,
    CalculationBase,
    CalculationCreate,
    CalculationUpdate,
    CalculationResponse,
)

__all__ = [
    "CalculationType",
    "CalculationBase",
    "CalculationCreate",
    "CalculationUpdate",
    "CalculationResponse",
]
