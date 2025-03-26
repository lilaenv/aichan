from discord import Colour, Embed, Interaction, TextChannel

from src.aichan._cli import parse_args_and_setup_logging
from src.aichan.database.dao.channel_dao import ChannelDAO
from src.aichan.discord.client import BotClient
from src.aichan.utils.decorators import *

client = BotClient.get_instance()
logger = parse_args_and_setup_logging()
channel_dao = ChannelDAO()


@client.tree.command(
    name="add_ch",
    description="Add a channel to the allowed command channels list",
)
# mypy(name-defined): defined in a wildcard import
@is_authorized_server()  # type: ignore # noqa: F405
# mypy(name-defined): defined in a wildcard import
@is_admin_user()  # type: ignore # noqa: F405
async def add_channel_command(
    interaction: Interaction,
    channel: TextChannel,
) -> None:
    """Add a channel to the allowed command channels list.

    Parameters
    ----------
    interaction : Interaction
        The Discord interaction object.
    channel : TextChannel
        The Discord channel to add to the allowed list.
    """
    try:
        if interaction.guild_id is None:
            await interaction.response.send_message(
                "このコマンドはサーバー内でのみ使用できます",
                ephemeral=True,
            )
            return

        await channel_dao.add_allowed_channel(
            channel_id=channel.id,
            guild_id=interaction.guild_id,
            added_by=interaction.user.id,
        )

        # ------ Define discord embed style ------
        embed = Embed(
            description=f"チャンネル <#{channel.id}> をコマンド実行可能リストに追加しました",
            color=0xF4B3C2,
        )
        # ----------------------------------------

        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(
            "%s added channel %s to allowed channels",
            interaction.user,
            channel.name,
        )
    except Exception as err:
        msg = f"An error occurred in the add_channel command: {err!s}"
        logger.exception(msg)
        await interaction.response.send_message(
            "**Error**: チャンネルの追加中にエラーが発生しました。管理者に報告してください。",
            ephemeral=True,
        )


@client.tree.command(
    name="rm_ch",
    description="Remove a channel from the allowed command channels list",
)
# mypy(name-defined): defined in a wildcard import
@is_authorized_server()  # type: ignore # noqa: F405
# mypy(name-defined): defined in a wildcard import
@is_admin_user()  # type: ignore # noqa: F405
async def remove_channel_command(
    interaction: Interaction,
    channel: TextChannel,
) -> None:
    """Remove a channel from the allowed command channels list.

    Parameters
    ----------
    interaction : Interaction
        The Discord interaction object.
    channel : TextChannel
        The Discord channel to remove from the allowed list.
    """
    try:
        if interaction.guild_id is None:
            await interaction.response.send_message(
                "このコマンドはサーバー内でのみ使用できます",
                ephemeral=True,
            )
            return

        removed = await channel_dao.remove_allowed_channel(channel_id=channel.id)

        if removed:
            # ------ Define discord embed style ------
            embed = Embed(
                description=f"チャンネル <#{channel.id}> をコマンド実行可能リストから削除しました",
                color=Colour.red(),
            )
            # ----------------------------------------

            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(
                "%s removed channel %s from allowed channels",
                interaction.user,
                channel.name,
            )
        else:
            await interaction.response.send_message(
                f"チャンネル <#{channel.id}> はコマンド実行可能リストに含まれていません",
                ephemeral=True,
            )
    except Exception as err:
        msg = f"An error occurred in the remove_channel command: {err!s}"
        logger.exception(msg)
        await interaction.response.send_message(
            "**Error**: チャンネルの削除中にエラーが発生しました。管理者に報告してください。",
            ephemeral=True,
        )


@client.tree.command(
    name="ls_ch",
    description="Show the list of channels that can execute commands",
)
# mypy(name-defined): defined in a wildcard import
@is_authorized_server()  # type: ignore # noqa: F405
# mypy(name-defined): defined in a wildcard import
@is_not_blocked_user()  # type: ignore # noqa: F405
async def list_channels_command(
    interaction: Interaction,
) -> None:
    """List all channels in the allowed command channels list.

    Parameters
    ----------
    interaction : Interaction
        The Discord interaction object.
    """
    try:
        if interaction.guild_id is None:
            await interaction.response.send_message(
                "このコマンドはサーバー内でのみ使用できます",
                ephemeral=True,
            )
            return

        allowed_channels = await channel_dao.get_allowed_channels(guild_id=interaction.guild_id)

        if not allowed_channels:
            await interaction.response.send_message(
                "コマンド実行可能なチャンネルが設定されていません。\n"
                "全てのチャンネルでコマンドを実行できます。",
                ephemeral=True,
            )
            return

        # ------ Define discord embed style ------
        embed = Embed(
            title="コマンド実行可能チャンネル一覧",
            description="以下のチャンネルでのみコマンドを実行できます",
            color=0xF4B3C2,
        )

        channels_text = "\n".join([f"<#{channel_id}>" for channel_id in allowed_channels])
        embed.add_field(name="チャンネル", value=channels_text)
        # ----------------------------------------

        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as err:
        msg = f"An error occurred in the list_channels command: {err!s}"
        logger.exception(msg)
        await interaction.response.send_message(
            "**Error**: チャンネル一覧の取得中にエラーが発生しました。管理者に報告してください。",
            ephemeral=True,
        )
