from discord import Interaction

from src.aichan._cli import parse_args_and_setup_logging
from src.aichan.adapters.chat import ChatMessage
from src.aichan.ai.models.gpt_model import GptModelParams
from src.aichan.ai.services.openai_text import generate_openai_response
from src.aichan.config.env import (
    CHAT_MODEL,
    GPT_DEFAULT_MAX_TOKENS,
    GPT_DEFAULT_TEMPERATURE,
    GPT_DEFAULT_TOP_P,
)
from src.aichan.config.prompt import CHAT_SYSTEM
from src.aichan.database.dao.limit_dao import UsageLimitDAO
from src.aichan.discord.client import BotClient
from src.aichan.utils.decorators import *
from src.aichan.utils.model_params_store import ModelParamsStore

client = BotClient.get_instance()
logger = parse_args_and_setup_logging()
model_params = ModelParamsStore()


@client.tree.command(
    name="chat",
    description="AIちゃんとチャットをします",
)
# mypy(name-defined): defined in a wildcard import
@is_authorized_server()  # type: ignore # noqa: F405
# mypy(name-defined): defined in a wildcard import
@is_not_blocked_user()  # type: ignore # noqa: F405
# mypy(name-defined): defined in a wildcard import
@has_daily_usage_left()  # type: ignore # noqa: F405
async def chat_command(
    interaction: Interaction,
    prompt: str,
) -> None:
    """Chat with bot."""
    try:
        user = interaction.user
        logger.info("%s executed 'chat' command: %s", user, prompt[:20])

        await interaction.response.defer()

        if CHAT_MODEL is None:
            await interaction.followup.send(
                "利用可能なモデルがありません。管理者に連絡してください。",
                ephemeral=True,
            )
            return

        params = GptModelParams(
            model=CHAT_MODEL,
            max_tokens=GPT_DEFAULT_MAX_TOKENS,
            temperature=GPT_DEFAULT_TEMPERATURE,
            top_p=GPT_DEFAULT_TOP_P,
        )

        message = [ChatMessage(role="user", content=prompt)]

        response_result = await generate_openai_response(
            system_prompt=CHAT_SYSTEM,
            prompt=message,
            model_params=params,
        )

        await interaction.followup.send(
            f"{response_result.result}",
        )

        await UsageLimitDAO().increment_usage_count(user.id)
    except Exception as err:
        msg = f"Error in chat command: {err!s}"
        logger.exception(msg)
        await interaction.followup.send(
            "エラーが発生しました。解決しない場合は管理者に連絡してください。",
            ephemeral=True,
        )
