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

    # 子クラスでプロパティをオーバーライドするための抽象メソッド定義
    # Abstract method definitions for property overrides in child classes
    @property
    @abstractmethod
    def model(self) -> app_commands.Choice[int] | str:
        """Get the model parameter."""
        pass

    @model.setter
    @abstractmethod
    def model(self, value: app_commands.Choice[int] | str) -> None:
        """Set and validate model."""
        pass

    @property
    @abstractmethod
    def max_tokens(self) -> int:
        """Get the max_tokens parameter."""
        pass

    @max_tokens.setter
    @abstractmethod
    def max_tokens(self, value: int) -> None:
        """Set and validate max_tokens."""
        pass

    @property
    @abstractmethod
    def temperature(self) -> float:
        """Get the temperature parameter."""
        pass

    @temperature.setter
    @abstractmethod
    def temperature(self, value: float) -> None:
        """Set and validate temperature."""
        pass

    @property
    @abstractmethod
    def top_p(self) -> float:
        """Get the top_p parameter."""
        pass

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
