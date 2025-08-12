from typing import TypeVar, Optional
from pydantic import BaseModel


class ErrorValidation(BaseModel):
    """
    Represents a validation error detail.

    Attributes:
        field (str): The name of the field that failed validation.
        message (str): The validation error message.
    """

    field: str
    message: str


T = TypeVar("T")


def check_not_empty(value: T, field_name: Optional[str]) -> T:
    """
    Validates that a value is not None or empty.

    Args:
        value (T): The value to validate.
        field_name (Optional[str]): The name of the field being validated.

    Returns:
        T: The original value if it's valid.

    Raises:
        ValueError: If the value is None or empty.
    """
    if value is None or value == "":
        raise ValueError(f"{field_name} cannot be empty")
    return value


def validate_uuid(value: str, field_name: str) -> str:
    """
    Validates that a string is a valid UUID (32 or 36 characters).

    Args:
        value (str): The string to validate.
        field_name (str): The name of the field being validated.

    Returns:
        str: The original string if it's a valid UUID.

    Raises:
        ValueError: If the string is not a valid UUID.
    """
    if not (len(value) in (32, 36) and value.replace("-", "").isalnum()):
        raise ValueError(f"{field_name} must be a valid 32 or 36 character UUID")
    return value
