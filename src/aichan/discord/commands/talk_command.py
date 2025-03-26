from typing import Literal

from discord import (
    Embed,
    HTTPException,
    Interaction,
    app_commands,
)

from src.aichan._cli import parse_args_and_setup_logging
from src.aichan.adapters.chat import ChatMessage
from src.aichan.adapters.response import send_response_result
from src.aichan.ai.models.claude_model import ClaudeModelParams
from src.aichan.ai.services.anthropic_text import generate_anthropic_response
from src.aichan.config.env import (
    CLAUDE_DEFAULT_MAX_TOKENS,
    CLAUDE_DEFAULT_TEMPERATURE,
    CLAUDE_DEFAULT_TOP_P,
    CLAUDE_MODELS,
)
from src.aichan.config.prompt import CLAUDE_SYSTEM
from src.aichan.database.dao.limit_dao import UsageLimitDAO
from src.aichan.discord.client import BotClient
from src.aichan.utils.decorators import *
from src.aichan.utils.model_params_store import ModelParamsStore

client = BotClient.get_instance()
logger = parse_args_and_setup_logging()
model_params = ModelParamsStore()

CLAUDE_THREAD_PREFIX: Literal[">>>"] = ">>>"
system_prompt_dict: dict[int, str] = {}


@client.tree.command(
    name="talk",
    description="スレッドを作成し、AIちゃんとの会話を開始します",
)
@app_commands.choices(
    model=[app_commands.Choice(name=model.name, value=model.value) for model in CLAUDE_MODELS],
)
# mypy(name-defined): defined in a wildcard import
@is_authorized_server()  # type: ignore # noqa: F405
# mypy(name-defined): defined in a wildcard import
@is_not_blocked_user()  # type: ignore # noqa: F405
# mypy(name-defined): defined in a wildcard import
@is_allowed_channel()  # type: ignore # noqa: F405
# mypy(name-defined): defined in a wildcard import
@has_daily_usage_left()  # type: ignore # noqa: F405
async def chat_command(
    interaction: Interaction,
    prompt: str,
    model: app_commands.Choice[int],
    temperature: float = CLAUDE_DEFAULT_TEMPERATURE,
    top_p: float = CLAUDE_DEFAULT_TOP_P,
) -> None:
    """Create a new thread and start a chat with the assistant.

    Parameters
    ----------
    interaction : Interaction
        The interaction object from the command.
    prompt : str
        The initial message to send to the AI assistant.
    model : app_commands.Choice[int]
        The AI model to use for the conversation.
    temperature : float
        Controls randomness in response generation. Lower values make responses more deterministic.
        Must be between 0.0 and 1.0. Defaults to predefined temperature value.
    top_p : float
        Controls diversity of responses by limiting token selection to a cumulative probability.
        Must be between 0.0 and 1.0. Defaults to predefined top_p value.
    """
    try:
        user = interaction.user
        logger.info("%s executed 'chat' command: %s", user, prompt[:20])

        if temperature < 0.0 or temperature > 1.0:
            await interaction.response.send_message(
                "**temperature**は 0.0 から1.0 の間で設定してください",
                ephemeral=True,
            )
            return
        if top_p < 0.0 or top_p > 1.0:
            await interaction.response.send_message(
                "**top_p**は 0.0 から1.0 の間で設定してください",
                ephemeral=True,
            )
            return

        # ------ Define discord embed style ------
        embed = Embed(
            description=f"<@{user.id}> **initiated the chat!**",
            color=0xF4B3C2,
        )
        embed.add_field(name="model", value=model.name, inline=True)
        embed.add_field(name="temperature", value=temperature, inline=True)
        embed.add_field(name="top_p", value=top_p, inline=True)
        embed.add_field(name="message", value=prompt)
        # ----------------------------------------

        await interaction.response.send_message(embed=embed)
        original_response = await interaction.original_response()

        # Create the thread
        thread = await original_response.create_thread(
            name=f"{CLAUDE_THREAD_PREFIX} {prompt[:30]}",
            auto_archive_duration=60,
            slowmode_delay=1,
        )
        system_prompt_dict[thread.id] = CLAUDE_SYSTEM
        model_params.set_model_params(
            thread.id,
            ClaudeModelParams(
                model=model.name,
                max_tokens=CLAUDE_DEFAULT_MAX_TOKENS,
                temperature=temperature,
                top_p=top_p,
            ),
        )
        async with thread.typing():
            messages = [ChatMessage(role=user.name, content=prompt)]
            response = await generate_anthropic_response(
                system_prompt=CLAUDE_SYSTEM,
                prompt=messages,
                model_params=model_params.get_model_params(thread.id),
            )

        # Increment the usage count for the user
        await UsageLimitDAO().increment_usage_count(user.id)

        await send_response_result(thread=thread, result=response)
    except HTTPException as err:
        msg = f"HTTPException occurred in the chat command: {err!s}"
        logger.exception(msg)
        await interaction.response.send_message(
            "**HTTPException**: 管理者に報告してください",
            ephemeral=True,
        )
    except Exception as err:
        msg = f"An error occurred in the chat command: {err!s}"
        logger.exception(msg)
        await interaction.response.send_message(
            "**Error**: 管理者に報告してください",
            ephemeral=True,
        )
