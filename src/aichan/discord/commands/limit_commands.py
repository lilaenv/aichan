from discord import Colour, Embed, Interaction

from src.aichan._cli import parse_args_and_setup_logging
from src.aichan.config.env import ADMIN_USER_IDS
from src.aichan.database.dao.access_dao import AccessDAO
from src.aichan.database.dao.limit_dao import UsageLimitDAO
from src.aichan.discord.client import BotClient
from src.aichan.utils.decorators import *

client = BotClient.get_instance()
logger = parse_args_and_setup_logging()


@client.tree.command(
    name="limit",
    description="Set the daily usage limit for all regular users",
)
# mypy(name-defined): defined in a wildcard import
@is_authorized_server()  # type: ignore # noqa: F405
# mypy(name-defined): defined in a wildcard import
@is_admin_user()  # type: ignore # noqa: F405
# mypy(name-defined): defined in a wildcard import
@is_allowed_channel()  # type: ignore # noqa: F405
async def limit_command(
    interaction: Interaction,
    limit: int,
) -> None:
    """Set the default daily usage limit for all regular users.

    Parameters
    ----------
    interaction : Interaction
        The interaction object from the command.
    limit : int
        The maximum number of AI calls allowed per day.
    """
    try:
        if limit < 1:
            await interaction.response.send_message(
                "**limit**は1以上の整数を指定してください",
                ephemeral=True,
            )
            return

        dao = UsageLimitDAO()
        await dao.set_default_daily_limit(limit)

        await interaction.response.send_message(
            f"AI使用回数の上限を{limit}/dayに設定しました",
            ephemeral=True,
        )
        logger.info(
            "%s set default daily limit to %d",
            interaction.user,
            limit,
        )
    except Exception:
        await interaction.response.send_message(
            "**Error**: 制限の設定中にエラーが発生しました。管理者に報告してください。",
            ephemeral=True,
        )
        logger.exception("An error occurred in the limit command")


@client.tree.command(
    name="ck_limit",
    description="AI使用回数の上限と現在の使用回数を確認します",
)
# mypy(name-defined): defined in a wildcard import
@is_authorized_server()  # type: ignore # noqa: F405
# mypy(name-defined): defined in a wildcard import
@is_not_blocked_user()  # type: ignore # noqa: F405
async def check_limit_command(
    interaction: Interaction,
) -> None:
    """Check the user's current usage and limit.

    Parameters
    ----------
    interaction : Interaction
        The interaction object from the command.
    """
    try:
        user = interaction.user
        dao = UsageLimitDAO()
        access_dao = AccessDAO()

        # advancedユーザーか管理者かどうかを確認
        is_admin = user.id in ADMIN_USER_IDS
        advanced_user_ids = await access_dao.fetch_user_ids_by_access_type(access_type="advanced")
        is_advanced = user.id in advanced_user_ids

        user_limit = await dao.get_user_daily_limit(user.id)
        current_usage = await dao.get_user_daily_usage(user.id)

        # ------ Define discord embed style ------
        embed = Embed(
            description=f"<@{user.id}> のコマンド使用状況",
            color=Colour.blue(),
        )

        # 通常ユーザーは回数制限あり、advancedユーザーと管理者は無制限
        if is_admin or is_advanced:
            embed.add_field(name="使用回数", value=f"{current_usage} / ∞", inline=True)
            embed.add_field(name="残り回数", value="∞", inline=True)
        else:
            embed.add_field(name="使用回数", value=f"{current_usage} / {user_limit}", inline=True)
            embed.add_field(name="残り回数", value=max(0, user_limit - current_usage), inline=True)

        embed.add_field(name="Note", value="使用回数は毎日0時にリセットされます", inline=False)
        # ----------------------------------------

        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception:
        await interaction.response.send_message(
            "**Error**: 使用状況の取得中にエラーが発生しました。管理者に報告してください。",
            ephemeral=True,
        )
        logger.exception("An error occurred in the check_limit command")
