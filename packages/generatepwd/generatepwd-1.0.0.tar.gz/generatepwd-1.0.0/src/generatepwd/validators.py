"""Module for input validators for password generation."""

from abc import ABC, abstractmethod

from .complexity import ComplexityLevel
from .password_exceptions import (InvalidComplexityException,
                                  InvalidLengthException)


class Validator(ABC):
    """Abstract base class for value validators."""

    @staticmethod
    @abstractmethod
    def validate(value):
        """validate values"""


class ComplexityValidator(Validator):
    """Validator for password complexity levels."""

    @staticmethod
    def validate(value: str):
        """Validate complexity against supported levels.

        Args:
            complexity (str): Complexity level provided by user.

        Raises:
            InvalidComplexityException: If complexity is invalid or empty.
        """
        if not any(True for item in ComplexityLevel.COMPLEXITY_LEVELS if value == item):
            raise InvalidComplexityException()
        if not value:
            raise InvalidComplexityException(
                "Complexity cannot be an empty list.")


class LengthValidator(Validator):
    """Validator for password length."""

    @staticmethod
    def validate(value: int):
        """Validate that length is an integer within allowed range.

        Args:
            length (int): Desired password length.

        Raises:
            InvalidLengthException: If length is not a positive integer <= 100.
        """
        if not isinstance(value, int):
            raise InvalidLengthException("Length must be an integer.")
        if value <= 0:
            raise InvalidLengthException("Length must be a positive integer.")
        if value > 100:
            raise InvalidLengthException()
