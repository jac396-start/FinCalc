# tests/unit/test_calculation.py

import pytest  # Import the pytest framework for writing and running tests
from typing import Union, List, Optional  # Import types for hinting
from uuid import uuid4
from datetime import datetime
from pydantic import ValidationError

# Import the calculator functions from the operations module
from app.operations import add, subtract, multiply, divide

# Import the schema definitions to be tested
from app.schemas.calculations import (
    CalculationBase,
    CalculationCreate,
    CalculationUpdate,
    CalculationResponse,
    CalculationType
)

# Define a type alias for numbers that can be either int or float
Number = Union[int, float]


# =============================================================================
# PART 1: Unit Tests for Calculator Operations
# =============================================================================

# ---------------------------------------------
# Unit Tests for the 'add' Function
# ---------------------------------------------

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (2, 3, 5),           # Test adding two positive integers
        (-2, -3, -5),        # Test adding two negative integers
        (2.5, 3.5, 6.0),     # Test adding two positive floats
        (-2.5, 3.5, 1.0),    # Test adding a negative float and a positive float
        (0, 0, 0),           # Test adding zeros
    ],
    ids=[
        "add_two_positive_integers",
        "add_two_negative_integers",
        "add_two_positive_floats",
        "add_negative_and_positive_float",
        "add_zeros",
    ]
)
def test_add(a: Number, b: Number, expected: Number) -> None:
    """
    Test the 'add' function with various combinations of integers and floats.
    """
    result = add(a, b)
    assert result == expected, f"Expected add({a}, {b}) to be {expected}, but got {result}"


# ---------------------------------------------
# Unit Tests for the 'subtract' Function
# ---------------------------------------------

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (5, 3, 2),           # Test subtracting a smaller positive integer from a larger one
        (-5, -3, -2),        # Test subtracting a negative integer from another negative integer
        (5.5, 2.5, 3.0),     # Test subtracting two positive floats
        (-5.5, -2.5, -3.0),  # Test subtracting two negative floats
        (0, 0, 0),           # Test subtracting zeros
    ],
    ids=[
        "subtract_two_positive_integers",
        "subtract_two_negative_integers",
        "subtract_two_positive_floats",
        "subtract_two_negative_floats",
        "subtract_zeros",
    ]
)
def test_subtract(a: Number, b: Number, expected: Number) -> None:
    """
    Test the 'subtract' function with various combinations of integers and floats.
    """
    result = subtract(a, b)
    assert result == expected, f"Expected subtract({a}, {b}) to be {expected}, but got {result}"


# ---------------------------------------------
# Unit Tests for the 'multiply' Function
# ---------------------------------------------

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (2, 3, 6),           # Test multiplying two positive integers
        (-2, 3, -6),         # Test multiplying a negative integer with a positive integer
        (2.5, 4.0, 10.0),    # Test multiplying two positive floats
        (-2.5, 4.0, -10.0),  # Test multiplying a negative float with a positive float
        (0, 5, 0),           # Test multiplying zero with a positive integer
    ],
    ids=[
        "multiply_two_positive_integers",
        "multiply_negative_and_positive_integer",
        "multiply_two_positive_floats",
        "multiply_negative_float_and_positive_float",
        "multiply_zero_and_positive_integer",
    ]
)
def test_multiply(a: Number, b: Number, expected: Number) -> None:
    """
    Test the 'multiply' function with various combinations of integers and floats.
    """
    result = multiply(a, b)
    assert result == expected, f"Expected multiply({a}, {b}) to be {expected}, but got {result}"


# ---------------------------------------------
# Unit Tests for the 'divide' Function
# ---------------------------------------------

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (6, 3, 2.0),           # Test dividing two positive integers
        (-6, 3, -2.0),         # Test dividing a negative integer by a positive integer
        (6.0, 3.0, 2.0),       # Test dividing two positive floats
        (-6.0, 3.0, -2.0),     # Test dividing a negative float by a positive float
        (0, 5, 0.0),           # Test dividing zero by a positive integer
    ],
    ids=[
        "divide_two_positive_integers",
        "divide_negative_integer_by_positive_integer",
        "divide_two_positive_floats",
        "divide_negative_float_by_positive_float",
        "divide_zero_by_positive_integer",
    ]
)
def test_divide(a: Number, b: Number, expected: float) -> None:
    """
    Test the 'divide' function with various combinations of integers and floats.
    """
    result = divide(a, b)
    assert result == expected, f"Expected divide({a}, {b}) to be {expected}, but got {result}"


# ---------------------------------------------
# Negative Test Case: Division by Zero
# ---------------------------------------------

def test_divide_by_zero() -> None:
    """
    Test the 'divide' function with division by zero.
    """
    with pytest.raises(ValueError) as excinfo:
        divide(6, 0)
    
    assert "Cannot divide by zero!" in str(excinfo.value)


# =============================================================================
# PART 2: Unit Tests for Calculation Schemas
# =============================================================================

# ---------------------------------------------
# Tests for CalculationBase Validation
# ---------------------------------------------

@pytest.mark.parametrize(
    "type_input, inputs, expected_type",
    [
        ("addition", [1, 2], CalculationType.ADDITION),
        ("ADDITION", [1, 2], CalculationType.ADDITION),  # Case insensitivity
        ("multiplication", [3.5, 2], CalculationType.MULTIPLICATION),
        ("division", [10, 2], CalculationType.DIVISION),
    ],
    ids=["valid_lowercase", "valid_uppercase", "valid_float_inputs", "valid_division"]
)
def test_calculation_base_valid(type_input: str, inputs: List[float], expected_type: CalculationType) -> None:
    """
    Test successful creation of CalculationBase with valid data.
    
    Verifies that:
    1. Valid types are accepted (case-insensitive).
    2. Inputs are stored correctly.
    """
    calc = CalculationBase(type=type_input, inputs=inputs)
    assert calc.type == expected_type
    assert calc.inputs == inputs

def test_calculation_base_invalid_inputs_count() -> None:
    """
    Test that validation fails when fewer than 2 inputs are provided.
    
    NOTE: Pydantic's 'min_items' validator triggers first (before custom validators),
    raising a standard error about list length.
    """
    with pytest.raises(ValidationError) as excinfo:
        CalculationBase(type="addition", inputs=[1])
    
    # Check for Pydantic's standard error message for min_items
    assert "List should have at least 2 items" in str(excinfo.value)

def test_calculation_base_division_by_zero() -> None:
    """
    Test that schema validation catches division by zero attempts.
    
    The schema should raise a ValueError if the operation is division
    and any number after the first is zero.
    """
    with pytest.raises(ValidationError) as excinfo:
        CalculationBase(type="division", inputs=[10, 0])
    assert "Cannot divide by zero" in str(excinfo.value)

def test_calculation_base_invalid_type() -> None:
    """
    Test that invalid calculation types are rejected.
    """
    with pytest.raises(ValidationError) as excinfo:
        CalculationBase(type="modulo", inputs=[10, 2])
    assert "Type must be one of" in str(excinfo.value)


# ---------------------------------------------
# Tests for CalculationCreate
# ---------------------------------------------

def test_calculation_create_requires_user_id() -> None:
    """
    Test that CalculationCreate requires a valid user_id UUID.
    """
    user_id = uuid4()
    calc = CalculationCreate(
        type="addition", 
        inputs=[1, 2], 
        user_id=user_id
    )
    assert calc.user_id == user_id

def test_calculation_create_missing_user_id() -> None:
    """
    Test that missing user_id raises a validation error.
    """
    with pytest.raises(ValidationError) as excinfo:
        CalculationCreate(type="addition", inputs=[1, 2])
    assert "Field required" in str(excinfo.value)


# ---------------------------------------------
# Tests for CalculationUpdate
# ---------------------------------------------

@pytest.mark.parametrize(
    "update_data",
    [
        {"inputs": [5, 5]},                # Update only inputs
        {"type": "subtraction"},           # Update only type
        {"type": "division", "inputs": [20, 2]} # Update both
    ],
    ids=["update_inputs_only", "update_type_only", "update_both"]
)
def test_calculation_update_partial(update_data: dict) -> None:
    """
    Test that CalculationUpdate supports partial updates.
    """
    update = CalculationUpdate(**update_data)
    for key, value in update_data.items():
        if key == "type":
            # Convert string input to Enum for comparison
            assert getattr(update, key) == CalculationType(value)
        else:
            assert getattr(update, key) == value

def test_calculation_update_validation_logic() -> None:
    """
    Test that validation logic (min items) applies to updates as well.
    """
    with pytest.raises(ValidationError) as excinfo:
        CalculationUpdate(inputs=[1]) # Too few items
    
    # Check for Pydantic's standard error message for min_items
    assert "List should have at least 2 items" in str(excinfo.value)


# ---------------------------------------------
# Tests for CalculationResponse
# ---------------------------------------------

def test_calculation_response_serialization() -> None:
    """
    Test that CalculationResponse correctly serializes all fields,
    including timestamps and IDs.
    """
    data = {
        "id": uuid4(),
        "user_id": uuid4(),
        "type": "addition",
        "inputs": [10, 5],
        "result": 15.0,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    response = CalculationResponse(**data)
    assert response.result == 15.0
    assert response.type == CalculationType.ADDITION
    assert isinstance(response.created_at, datetime)
