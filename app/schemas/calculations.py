"""
Calculation Schemas Module

This module defines the Pydantic schemas for validation and serialization of calculation data.
It includes schemas for:
- Base calculation data (common fields)
- Creating new calculations
- Updating existing calculations
- Returning calculation responses

The schemas use Pydantic's validation system to ensure data integrity and provide
clear error messages when validation fails.
"""

from enum import Enum
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from pydantic import (
    BaseModel, 
    Field, 
    ConfigDict, 
    model_validator, 
    field_validator
)

class CalculationType(str, Enum):
    """
    Enumeration of valid calculation types.
    
    Using an Enum provides type safety and ensures that only valid
    calculation types are accepted. The str base class ensures that
    the values are serialized as strings in JSON.
    """
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"

class CalculationBase(BaseModel):
    """
    Base schema for calculation data.
    This schema defines the common fields that all calculation operations share:
    - type: The type of calculation (addition, subtraction, etc.)
    - inputs: A list of numeric values to operate on
    """
    type: CalculationType = Field(
        ...,
        description="Type of calculation (addition, subtraction, multiplication, division)",
        example="addition"
    )
    inputs: List[float] = Field(
        ...,
        description="List of numeric inputs for the calculation",
        example=[10.5, 3, 2],
        min_items=2  # Ensures at least 2 numbers are provided
    )

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v):
        """
        Validates the calculation type before conversion to an enum.
        Ensures the input is a string and matches allowed types (case-insensitive).
        """
        allowed = {e.value for e in CalculationType}
        if not isinstance(v, str) or v.lower() not in allowed:
            raise ValueError(f"Type must be one of: {', '.join(sorted(allowed))}")
        return v.lower()

    @field_validator("inputs", mode="before")
    @classmethod
    def check_inputs_is_list(cls, v):
        """
        Validates that the inputs field is a list before type conversion.
        """
        if not isinstance(v, list):
            raise ValueError("Input should be a valid list")
        return v

    @model_validator(mode='after')
    def validate_inputs(self) -> "CalculationBase":
        """
        Validates the inputs based on calculation type.
        1. Ensures there are at least 2 numbers.
        2. For division, ensures no divisor is zero.
        """
        if len(self.inputs) < 2:
            raise ValueError("At least two numbers are required for calculation")
        
        if self.type == CalculationType.DIVISION:
            # Prevent division by zero (skip the first value as it is the numerator)
            if any(x == 0 for x in self.inputs[1:]):
                raise ValueError("Cannot divide by zero")
        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"type": "addition", "inputs": [10.5, 3, 2]},
                {"type": "division", "inputs": [100, 2]}
            ]
        }
    )

class CalculationCreate(CalculationBase):
    """
    Schema for creating a new Calculation.
    Extends base schema with a user_id field for database insertion.
    """
    user_id: UUID = Field(
        ...,
        description="UUID of the user who owns this calculation",
        example="123e4567-e89b-12d3-a456-426614174000"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "addition",
                "inputs": [10.5, 3, 2],
                "user_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )

class CalculationUpdate(BaseModel):
    """
    Schema for updating an existing Calculation.
    Allows partial updates of 'type' and 'inputs'.
    """
    type: Optional[CalculationType] = Field(
        None,
        description="(Optional) New calculation type",
        example="addition"
    )

    inputs: Optional[List[float]] = Field(
        None,
        description="Updated list of numeric inputs for the calculation",
        example=[42, 7],
        min_items=2
    )

    @model_validator(mode='after')
    def validate_inputs(self) -> "CalculationUpdate":
        """
        Validates the inputs if they are being updated.
        """
        if self.inputs is not None and len(self.inputs) < 2:
            raise ValueError("At least two numbers are required for calculation")
        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "type": "addition", 
                "inputs": [42, 7]
            }
        }
    )

class CalculationResponse(CalculationBase):
    """
    Schema for reading a Calculation from the database.
    Includes database identifiers (id, user_id), timestamps, and the result.
    """
    id: UUID = Field(
        ...,
        description="Unique UUID of the calculation",
        example="123e4567-e89b-12d3-a456-426614174999"
    )
    user_id: UUID = Field(
        ...,
        description="UUID of the user who owns this calculation",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    created_at: datetime = Field(
        ..., 
        description="Time when the calculation was created"
    )
    updated_at: datetime = Field(
        ..., 
        description="Time when the calculation was last updated"
    )
    result: float = Field(
        ...,
        description="Result of the calculation",
        example=15.5
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174999",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "addition",
                "inputs": [10.5, 3, 2],
                "result": 15.5,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            }
        }
    )
