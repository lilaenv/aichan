from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import app_commands


class ModelParamsBase(ABC):
    """Base class for AI model parameters.

    This abstract class defines the common interface and validation
    logic for all AI model parameter classes.
    """

    def __init__(
        self,
        model: app_commands.Choice[int] | str,
        max_tokens: int,
        temperature: float,
        top_p: float,
    ) -> None:
        """Initialize model parameters.

        Parameters
        ----------
        model : app_commands.Choice[int] | str
            The model to use.
        max_tokens : int
            The maximum number of tokens to generate.
        temperature : float
            The sampling temperature.
        top_p : float
            The nucleus sampling parameter.
        """
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

    @property
    def model(self) -> app_commands.Choice[int] | str:
        # mypy(no-any-return): the return type of the property is clearly an int
        # mypy(attr-defined): the subclass setter will be called first,
        # ensuring that _model is always defined before it's accessed.
        return self._model  # type: ignore

    @model.setter
    @abstractmethod
    def model(self, value: app_commands.Choice[int]) -> None:
        """Set and validate model.

        Parameters
        ----------
        value : app_commands.Choice[int]
            The model to use.

        Raises
        ------
        ValueError
            If value is not a valid model.
        """

    @property
    def max_tokens(self) -> int:
        # mypy(no-any-return): the return type of the property is clearly an int
        # mypy(attr-defined): the subclass setter will be called first,
        # ensuring that _max_tokens is always defined before it's accessed.
        return self._max_tokens  # type: ignore

    @max_tokens.setter
    @abstractmethod
    def max_tokens(self, value: int) -> None:
        """Set and validate max_tokens.

        Parameters
        ----------
        value : int
            The maximum number of tokens to generate.

        Raises
        ------
        ValueError
            If value is outside the valid range for the model.
        """

    @property
    def temperature(self) -> float:
        # the return type of the property is clearly an float
        # the subclass setter will be called first,
        # ensuring that _temperature is always defined before it's accessed.
        return self._temperature  # type: ignore

    @temperature.setter
    @abstractmethod
    def temperature(self, value: float) -> None:
        """Set and validate temperature.

        Parameters
        ----------
        value : float
            The sampling temperature.

        Raises
        ------
        ValueError
            If value is outside the valid range for the model.
        """

    @property
    def top_p(self) -> float:
        return self._top_p

    @top_p.setter
    def top_p(self, value: float) -> None:
        """Set and validate top_p.

        Parameters
        ----------
        value : float
            The nucleus sampling parameter.

        Raises
        ------
        ValueError
            If value is outside the valid range 0.0 and 1.0.
        """
        if not (0.0 <= value <= 1.0):
            msg = "The top_p must be between 0.0 and 1.0."
            raise ValueError(msg)
        self._top_p = value
