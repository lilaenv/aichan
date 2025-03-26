from collections.abc import Callable
from typing import TypeVar, cast

from discord import Interaction, app_commands

from src.aichan.config.env import ADMIN_USER_IDS, AUTHORIZED_SERVER_IDS
from src.aichan.database.dao.access_dao import AccessDAO
from src.aichan.database.dao.channel_dao import ChannelDAO
from src.aichan.database.dao.limit_dao import UsageLimitDAO

_T = TypeVar("_T")


def is_admin_user() -> Callable[[_T], _T]:
    """Check if the user has administrative access permission.

    Returns
    -------
    Callable[[_T], _T]
        A decorator checks whether the user executing command is listed
        in the environment variable `ADMIN_USER_IDS`.
    """

    def predicate(interaction: Interaction) -> bool:
        return interaction.user.id in ADMIN_USER_IDS

    return app_commands.check(predicate)


def is_advanced_user() -> Callable[[_T], _T]:
    """Check if the user has advanced access permission.

    Returns
    -------
    Callable[[_T], _T]
        A decorator checks whether the user executing command is listed
        in the table `access` with the access type `advanced`.
    """

    async def predicate(interaction: Interaction) -> bool:
        advanced_user_ids = await AccessDAO().fetch_user_ids_by_access_type(access_type="advanced")
        return interaction.user.id in advanced_user_ids

    return app_commands.check(predicate)


def is_authorized_server() -> Callable[[_T], _T]:
    """Check if the server has been authorized by bot owner.

    Returns
    -------
    Callable[[_T], _T]
        A decorator checks whether the server is listed in the
        environment variable `AUTHORIZED_SERVER_IDS`.
    """

    def predicate(interaction: Interaction) -> bool:
        return interaction.guild_id in AUTHORIZED_SERVER_IDS

    return app_commands.check(predicate)


def is_not_blocked_user() -> Callable[[_T], _T]:
    """Check if user has not been blocked.

    Returns
    -------
    Callable[[_T], _T]
        A decorator checks whether the user executing command is not
        listed in the table `access` with the access type `blocked`.
    """

    async def predicate(interaction: Interaction) -> bool:
        blocked_user_ids = await AccessDAO().fetch_user_ids_by_access_type(access_type="blocked")
        return interaction.user.id not in blocked_user_ids

    return app_commands.check(predicate)


def has_daily_usage_left() -> Callable[[_T], _T]:
    """Check if the user has not reached their daily usage limit.

    Returns
    -------
    Callable[[_T], _T]
        A decorator that checks whether the user has not reached
        their daily limit of API calls.
    """

    async def predicate(interaction: Interaction) -> bool:
        # Admin users bypass usage limits
        if interaction.user.id in ADMIN_USER_IDS:
            return True

        # Advanced users bypass usage limits
        advanced_user_ids = await AccessDAO().fetch_user_ids_by_access_type(access_type="advanced")
        if interaction.user.id in advanced_user_ids:
            return True

        # Check usage limits for regular users
        dao = UsageLimitDAO()
        current_usage = await dao.get_user_daily_usage(interaction.user.id)
        user_limit = await dao.get_user_daily_limit(interaction.user.id)

        return cast("bool", current_usage < user_limit)

    return app_commands.check(predicate)


# This function is used in the on_message event handler for Discord messages
async def check_user_daily_limit(user_id: int) -> bool:
    """Check if a user has reached their daily API usage limit.

    Parameters
    ----------
    user_id : int
        The Discord user ID to check

    Returns
    -------
    bool
        True if the user has not reached their limit, False if they have
    """
    # Admin users bypass usage limits
    if user_id in ADMIN_USER_IDS:
        return True

    # Advanced users bypass usage limits
    advanced_user_ids = await AccessDAO().fetch_user_ids_by_access_type(access_type="advanced")
    if user_id in advanced_user_ids:
        return True

    # Check usage limits for regular users
    dao = UsageLimitDAO()
    current_usage = await dao.get_user_daily_usage(user_id)
    user_limit = await dao.get_user_daily_limit(user_id)

    return cast("bool", current_usage < user_limit)


def is_allowed_channel() -> Callable[[_T], _T]:
    """Check if the command is executed in an allowed channel.

    Returns
    -------
    Callable[[_T], _T]
        A decorator that checks whether the channel is allowed for command execution.
        If no channels are specified, all channels are allowed.
        Admin users can bypass this check.
    """

    async def predicate(interaction: Interaction) -> bool:
        # Admin users bypass channel restrictions
        if interaction.user.id in ADMIN_USER_IDS:
            return True

        # Get the channel ID from the interaction
        channel_id = interaction.channel_id
        if channel_id is None:
            return False

        # Check if there are any allowed channels for this guild
        channel_dao = ChannelDAO()
        if interaction.guild_id is not None:
            allowed_channels = await channel_dao.get_allowed_channels(
                guild_id=interaction.guild_id,
            )

            # If there are no allowed channels specified, all channels are allowed
            if not allowed_channels:
                return True

            # Otherwise, check if this channel is in the allowed list
            return channel_id in allowed_channels

        return False

    return app_commands.check(predicate)
