"""Module containing type validation utilities."""
from .type_validation import (
    # Type guards for conditional checking
    is_type,
    is_not_none,

    # Assertion functions (NASA-style)
    assert_type,
    assert_not_none,
    assert_range,
    assert_length,
    assert_numeric,
    assert_string_like,
    assert_sequence,
    assert_mapping,
    assert_path,
    assert_boolean,

    # Exceptions
    TypeAssertionError,

    # Decorator
    type_checked
)

__all__ = [
    "is_type",
    "is_not_none",
    "assert_type",
    "assert_not_none",
    "assert_range",
    "assert_length",
    "assert_numeric",
    "assert_string_like",
    "assert_sequence",
    "assert_mapping",
    "assert_path",
    "assert_boolean",
    "TypeAssertionError",
    "type_checked"
]
