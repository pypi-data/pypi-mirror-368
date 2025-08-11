"""Module for calculating character distribution based on complexity levels."""
from dataclasses import dataclass

from .complexity import ComplexityLevel
from .password_exceptions import InvalidComplexityException


@dataclass
class AlphaCharacterDistribution:
    """Represents counts of uppercase and lowercase characters for password distribution."""
    uppercase_length: int
    lowercase_length: int


class CharacterDistributionCalculator:
    """Calculator for splitting password length into uppercase and lowercase counts based on complexity."""

    @staticmethod
    def get_upper_lower_case_length_by_complexity(complexity: str, length: int) -> AlphaCharacterDistribution:
        """Determine uppercase and lowercase counts based on complexity and total length.

        Args:
            complexity (str): Complexity level (SIMPLE, MEDIUM, HIGH).
            length (int): Total desired password length.

        Returns:
            AlphaCharacterDistribution: Object with uppercase_length and lowercase_length.

        Raises:
            ValueError: If complexity level is invalid.
        """
        if complexity == ComplexityLevel.SIMPLE:
            return AlphaCharacterDistribution(0, length)

        if complexity == ComplexityLevel.MEDIUM:
            if length % 2 == 0:
                return AlphaCharacterDistribution(length // 2, length // 2)

            uppercase_length = sum(divmod(length, 2))
            lowercase_length = length - uppercase_length
            return AlphaCharacterDistribution(uppercase_length, lowercase_length)

        if complexity == ComplexityLevel.HIGH:
            alpha_length = length - 2
            if alpha_length % 2 != 0:
                uppercase_length = sum(divmod(alpha_length, 2))
                lowercase_length = alpha_length - uppercase_length
                return AlphaCharacterDistribution(uppercase_length, lowercase_length)
            return AlphaCharacterDistribution(alpha_length // 2, alpha_length // 2)

        raise InvalidComplexityException("Invalid complexity level provided.")
