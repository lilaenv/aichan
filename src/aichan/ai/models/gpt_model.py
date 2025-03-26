from __future__ import annotations

from typing import TYPE_CHECKING

from src.aichan.ai.models._base import ModelParamsBase

if TYPE_CHECKING:
    from discord import app_commands


class GptModelParams(ModelParamsBase):
    """Parameters for GPT AI model.

    Parameters
    ----------
    model : app_commands.Choice[int] | str
        The model to use.
    max_tokens : int
        The maximum number of tokens that can be generated in the
        completion. Must be between 0 and 16384.
    temperature : float
        The temperature parameter for sampling, controlling randomness.
        Must be between 0.0 and 2.0.
    top_p : float
        The top-p sampling parameter, controlling diversity. Must be
        between 0.0 and 1.0.
    """

    @ModelParamsBase.model.setter
    def model(self, value: app_commands.Choice[int] | str) -> None:
        """Set and validate model."""
        self._model = value

    @ModelParamsBase.max_tokens.setter
    def max_tokens(self, value: int) -> None:
        """Set and validate max_tokens."""
        # GPT's max_tokens must be between 1 and 16384
        if not 1 <= value <= 16384:  # noqa: PLR2004
            msg = "max_tokens must be between 1 and 16384"
            raise ValueError(msg)
        self._max_tokens = value

    @ModelParamsBase.temperature.setter
    def temperature(self, value: float) -> None:
        """Set and validate temperature."""
        # GPT's temperature must be between 0.0 and 2.0
        if not 0.0 <= value <= 2.0:  # noqa: PLR2004
            msg = "temperature must be between 0.0 and 2.0"
            raise ValueError(msg)
        self._temperature = value

    @ModelParamsBase.top_p.setter
    def top_p(self, value: float) -> None:
        """Set and validate top_p."""
        # GPT's top_p must be between 0.0 and 1.0
        if not 0.0 <= value <= 1.0:
            msg = "top_p must be between 0.0 and 1.0"
            raise ValueError(msg)
        self._top_p = value
