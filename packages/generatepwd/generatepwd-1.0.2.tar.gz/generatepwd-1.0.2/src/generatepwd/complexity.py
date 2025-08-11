"""Module for defining complexity levels and strategies for password generation."""

import random
import string
from abc import ABC, abstractmethod


class ComplexityLevel:
    """Supported password complexity levels."""

    SIMPLE = 'SIMPLE'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    COMPLEXITY_LEVELS = (SIMPLE, MEDIUM, HIGH)


class ComplexityStrategy(ABC):
    """Base class for password complexity strategies."""

    @staticmethod
    @abstractmethod
    def generate_password(lowercase_length: int, uppercase_length: int):
        """Generate password segments based on length parameters.

        Args:
            lowercase_length (int): Number of lowercase characters.
            uppercase_length (int): Number of uppercase characters.

        Returns:
            str: Generated password segment.
        """


class SimpleComplexityStrategy(ComplexityStrategy):
    """Strategy for generating simple (lowercase only) passwords."""

    @staticmethod
    def generate_password(lowercase_length: int, uppercase_length=None) -> str:
        """Generate a password with lowercase letters only.

        Args:
            lowercase_length (int): Number of lowercase characters.

        Returns:
            str: Generated password string.
        """
        all_characters = ''.join(string.ascii_lowercase)
        result = ''.join(random.choice(all_characters)
                         for _ in range(lowercase_length))
        return result


class MediumComplexityStrategy(ComplexityStrategy):
    """Strategy for generating medium complexity (mixed case) passwords."""

    @staticmethod
    def generate_password(lowercase_length: int, uppercase_length: int) -> str:
        """Generate a password with mixed lowercase and uppercase letters.

        Args:
            lowercase_length (int): Number of lowercase characters.
            uppercase_length (int): Number of uppercase characters.

        Returns:
            str: Generated password string.
        """
        lowercase_random_chars = ''.join(random.choice(
            string.ascii_lowercase) for _ in range(lowercase_length))
        uppercase_random_chars = ''.join(random.choice(
            string.ascii_uppercase) for _ in range(uppercase_length))
        result = ''.join(random.sample(
            lowercase_random_chars + uppercase_random_chars, lowercase_length + uppercase_length))
        return result


class HighComplexityStrategy(ComplexityStrategy):
    """Strategy for generating high complexity (mixed case, digits, special) passwords."""

    @staticmethod
    def generate_password(lowercase_length: int, uppercase_length: int) -> str:
        """Generate a password with lowercase, uppercase, digits, and special characters.

        Args:
            lowercase_length (int): Number of lowercase characters.
            uppercase_length (int): Number of uppercase characters.

        Returns:
            str: Generated password string.
        """
        random_digit = ''.join(random.choice(string.digits) for _ in range(1))
        random_special_char = ''.join(random.choice(
            string.punctuation) for _ in range(1))
        lowercase_random_chars = ''.join(random.choice(
            string.ascii_lowercase) for _ in range(lowercase_length))
        uppercase_random_chars = ''.join(random.choice(
            string.ascii_uppercase) for _ in range(uppercase_length))
        all_characters = lowercase_random_chars + \
            uppercase_random_chars + random_digit + random_special_char
        result = ''.join(random.sample(all_characters, len(all_characters)))
        return result
