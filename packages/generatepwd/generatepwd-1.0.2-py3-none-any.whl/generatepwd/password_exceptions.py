"""Module defining exceptions for password generation errors."""


class PasswordGenerationException(Exception):
    """Base exception for password generation errors."""


class InvalidComplexityException(PasswordGenerationException):
    """Exception raised for invalid complexity levels."""

    def __init__(self, message: str = "Complexity must be one of the following: SIMPLE, MEDIUM, HIGH."):
        super().__init__(message)


class InvalidLengthException(PasswordGenerationException):
    """Exception raised for invalid password length."""

    def __init__(self, message: str = "Length must be a positive integer and not exceed 100 characters."):
        super().__init__(message)
