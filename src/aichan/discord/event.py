from discord import Colour, Embed, Interaction, Thread, app_commands
from discord import Message as DiscordMessage

from src.aichan._cli import parse_args_and_setup_logging
from src.aichan.adapters.chat import ChatMessage
from src.aichan.adapters.response import send_response_result
from src.aichan.ai.services.anthropic_text import generate_anthropic_response
from src.aichan.config.env import CLAUDE_DEFAULT_CONTEXT_WINDOW
from src.aichan.database.dao.access_dao import AccessDAO
from src.aichan.database.dao.limit_dao import UsageLimitDAO
from src.aichan.discord.client import BotClient
from src.aichan.discord.commands import *

client = BotClient.get_instance()
logger = parse_args_and_setup_logging()


async def _close_thread(thread: Thread) -> None:
    await thread.send(
        embed=Embed(
            description="context reached limit, closing thread",
            color=Colour.light_grey(),
        ),
    )
    await thread.edit(archived=False, locked=True)


async def _get_conversation_history(thread: Thread, limit: int) -> list:
    convo_history = [
        await ChatMessage.from_discord_message(message)
        async for message in thread.history(limit=limit)
    ]
    convo_history = [msg for msg in convo_history if msg is not None]
    convo_history.reverse()
    return convo_history


async def _handle_claude_thread(discord_msg: DiscordMessage) -> None:
    if not isinstance(discord_msg.channel, Thread):
        return

    thread: Thread = discord_msg.channel

    if thread.message_count > CLAUDE_DEFAULT_CONTEXT_WINDOW:
        await _close_thread(thread)
        return

    # mypy(name-defined): defined in a wildcard import
    if not await check_user_daily_limit(discord_msg.author.id):  # type: ignore # noqa: F405
        await thread.send(
            embed=Embed(
                description="**本日のAI使用回数の上限に達しました。明日0時にリセットされます。**",
                color=Colour.red(),
            ),
        )
        return

    try:
        convo_history = await _get_conversation_history(thread, CLAUDE_DEFAULT_CONTEXT_WINDOW)

        async with thread.typing():
            # mypy(name-defined): defined in a wildcard import
            response = await generate_anthropic_response(  # type: ignore
                # mypy(name-defined): defined in a wildcard import
                system_prompt=system_prompt_dict.get(  # type: ignore # noqa: F405
                    thread.id,
                ),
                prompt=convo_history,
                # mypy(name-defined): defined in a wildcard import
                model_params=model_params.get_model_params(  # type: ignore # noqa: F405
                    thread.id,
                ),
            )

        # Increment usage count
        await UsageLimitDAO().increment_usage_count(discord_msg.author.id)

        await send_response_result(thread=discord_msg.channel, result=response)
    except Exception as err:
        error_msg = f"Error occurred while processing message: {err!s}"
        logger.exception(error_msg)

        await thread.send(
            embed=Embed(
                description="**Error:** 応答の生成中にエラーが発生しました",
                color=Colour.red(),
            ),
        )


async def _is_valid_message(discord_msg: DiscordMessage) -> bool:
    # Get the user id that has access type "blocked"
    blocked_user_ids = await AccessDAO().fetch_user_ids_by_access_type(access_type="blocked")

    return not (
        # Ignore messages from the bot
        # Blocked user can't use the bot
        # Ignore messages not in a thread
        # Ignore threads not created by the bot
        # Ignore threads that are archived, locked or title is not what we expected
        # Ignore threads that have too many messages
        discord_msg.author == client.user
        or discord_msg.author.id in blocked_user_ids
        or not isinstance(discord_msg.channel, Thread)
        or discord_msg.channel.owner_id != client.user.id
        or discord_msg.channel.archived
        or discord_msg.channel.locked
    )


@client.event
async def on_message(user_msg: DiscordMessage) -> None:
    """Event handler for Discord message events.

    Parameters
    ----------
    user_msg : DiscordMessage
        A message received from discord.
    """
    try:
        if not await _is_valid_message(user_msg):
            return

        # Chat with claude
        if isinstance(user_msg.channel, Thread) and user_msg.channel.name.startswith(
            # mypy(name-defined): defined in a wildcard import
            CLAUDE_THREAD_PREFIX,  # type: ignore # noqa: F405
        ):
            await _handle_claude_thread(user_msg)
    except Exception:
        logger.exception("An error occurred in the on_message event")
        await user_msg.channel.send(
            embed=Embed(
                description="An error occurred. Please try again later.",
                color=Colour.red(),
            ),
        )


@client.tree.error
async def on_app_command_error(
    interaction: Interaction,
    error: app_commands.AppCommandError,
) -> None:
    """Process errors that occur during application command execution.

    Parameters
    ----------
    interaction : Interaction
        Object containing information about the interaction between the
        user and the bot
    error : app_commands.AppCommandError
        The error object that was raised
    """
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message(
            "**CheckFailure:** このコマンドを実行する権限がありません",
            ephemeral=True,
        )
