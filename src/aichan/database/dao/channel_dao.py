import datetime

import aiosqlite

from src.aichan.config.timezone import TIMEZONE
from src.aichan.database._dao_base import SQLiteDaoBase


class ChannelDAO(SQLiteDaoBase):
    """Data Access Object for managing allowed command channels.

    Attributes
    ----------
    _table_name : str
        Name of the database table for allowed channels.
    """

    _table_name = "allowed_channels"

    async def create_table(self) -> None:
        """Create table if it doesn't exist.

        Raises
        ------
        ValueError
            If the table name contains invalid characters
        """
        if not self.validate_table_name(self._table_name):
            msg = "Invalid table name: Only alphanumeric characters and underscores are allowed."
            raise ValueError(msg)

        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = f"""
            CREATE TABLE IF NOT EXISTS {self._table_name} (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER NOT NULL UNIQUE,
                guild_id   INTEGER NOT NULL,
                added_at   TIMESTAMP NOT NULL,
                added_by   INTEGER NOT NULL
            );
            """
            await conn.execute(query)
            await conn.commit()
        finally:
            await conn.close()

    async def add_allowed_channel(self, channel_id: int, guild_id: int, added_by: int) -> None:
        """Add a channel to the allowed channels list.

        Parameters
        ----------
        channel_id : int
            ID of the Discord channel.
        guild_id : int
            ID of the Discord guild/server.
        added_by : int
            ID of the user who added the channel.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        now = datetime.datetime.now(TIMEZONE)
        try:
            query = """
            INSERT INTO allowed_channels (channel_id, guild_id, added_at, added_by)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(channel_id) DO UPDATE SET
                guild_id = ?,
                added_at = ?,
                added_by = ?
            """
            await conn.execute(
                query,
                (channel_id, guild_id, now, added_by, guild_id, now, added_by),
            )
            await conn.commit()
        finally:
            await conn.close()

    async def remove_allowed_channel(self, channel_id: int) -> bool:
        """Remove a channel from the allowed channels list.

        Parameters
        ----------
        channel_id : int
            ID of the Discord channel.

        Returns
        -------
        bool
            True if the channel was removed, False if it wasn't found.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = """
            DELETE FROM allowed_channels WHERE channel_id = ?
            """
            cursor = await conn.execute(query, (channel_id,))
            await conn.commit()
            return cursor.rowcount > 0
        finally:
            await conn.close()

    async def is_channel_allowed(self, channel_id: int) -> bool:
        """Check if a channel is in the allowed channels list.

        Parameters
        ----------
        channel_id : int
            ID of the Discord channel.

        Returns
        -------
        bool
            True if the channel is allowed, False otherwise.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = """
            SELECT 1 FROM allowed_channels WHERE channel_id = ?
            """
            cursor = await conn.execute(query, (channel_id,))
            result = await cursor.fetchone()
            return result is not None
        finally:
            await conn.close()

    async def get_allowed_channels(self, guild_id: int) -> list[int]:
        """Get all allowed channels for a guild.

        Parameters
        ----------
        guild_id : int
            ID of the Discord guild/server.

        Returns
        -------
        list[int]
            List of allowed channel IDs.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = """
            SELECT channel_id FROM allowed_channels WHERE guild_id = ?
            """
            cursor = await conn.execute(query, (guild_id,))
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
        finally:
            await conn.close()
