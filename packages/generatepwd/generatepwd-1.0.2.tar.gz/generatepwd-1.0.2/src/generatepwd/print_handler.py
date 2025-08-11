"""Module for handling CLI output formatting for errors and passwords."""

from typing import Any

import click


class PrintHandler:
    """Handles the printing of errors and generated passwords in the CLI."""

    @staticmethod
    def print_error(error: Any):
        """Print an error message in red to the CLI.

        Args:
            error (Exception or str): Error to display.
        """
        click.echo(click.style(f"Error: {error}", fg='red'))

    @staticmethod
    def print_password(password: str):
        """Print the generated password in green to the CLI.

        Args:
            password (str): Generated password.
        """
        click.echo(click.style(f"Generated Password: {password}", fg='green'))

    @staticmethod
    def print_complexity_help():
        """Print help message describing complexity levels."""
        click.echo(click.style(
            "Complexity Levels:\n"
            "SIMPLE: Only lowercase letters.\n"
            "MEDIUM: Equal mix of uppercase and lowercase letters.\n"
            "HIGH: Mix of uppercase, lowercase, digits, and special characters.",
            fg='blue'))
