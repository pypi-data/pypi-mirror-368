"""Service classes for the ``obk`` CLI."""

from __future__ import annotations


class ObkError(Exception):
    """Base error for the ``obk`` CLI."""


class DivisionByZeroError(ObkError):
    """Raised when attempting to divide by zero."""


class FatalError(ObkError):
    """Raised to trigger a fatal failure."""


class Greeter:
    """Simple greeter service."""

    def hello(self) -> str:
        """Return a generic hello world string."""

        return "hello world"

    def greet(self, name: str, excited: bool = False) -> str:
        """Return a greeting for ``name``.

        Parameters
        ----------
        name:
            Name of the person to greet.
        excited:
            Whether to add excitement to the greeting.
        """

        if excited:
            return f"Hello, {name}!!!"
        return f"Hello, {name}."


class Divider:
    """Perform division with error handling."""

    def divide(self, a: float, b: float) -> float:
        """Return ``a`` divided by ``b``.

        Raises
        ------
        DivisionByZeroError
            If ``b`` is zero.
        """

        if b == 0:
            raise DivisionByZeroError("cannot divide by zero")
        return a / b
