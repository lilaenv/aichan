import datetime

import aiosqlite

from src.aichan.config.timezone import TIMEZONE
from src.aichan.database._dao_base import SQLiteDaoBase


class AccessDAO(SQLiteDaoBase):
    """Data Access Object for managing user access rights.

    Attributes
    ----------
    _table_name : str
        Name of the database table for access rights.
    """

    _table_name = "access"

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
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                access_type TEXT NOT NULL,
                granted_at  DATE NOT NULL,
                disabled_at DATE DEFAULT NULL
            );
            """
            await conn.execute(query)
            await conn.commit()
        finally:
            await conn.close()

    async def insert(self, user_id: int, access_type: str) -> None:
        """Insert a new access right record for a user.

        Parameters
        ----------
        user_id : int
            ID of the user receiving access rights.
        access_type : str
            Type of access being granted.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        date = datetime.datetime.now(TIMEZONE).date()
        try:
            query = """
            INSERT INTO access (user_id, access_type, granted_at)
            VALUES (?, ?, ?);
            """
            await conn.execute(query, (user_id, access_type, date))
            await conn.commit()
        finally:
            await conn.close()

    async def fetch_user_ids_by_access_type(self, access_type: str) -> list[int]:
        """Fetch IDs of users who have a specific active access type.

        Parameters
        ----------
        access_type : str
            Type of access to filter by.

        Returns
        -------
        list[int]
            List of user IDs with the specified active access type.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = """
            SELECT user_id FROM access WHERE access_type = ? AND disabled_at IS NULL;
            """
            cursor = await conn.execute(query, (access_type,))
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
        finally:
            await conn.close()

    async def disable(self, user_id: int, access_type: str) -> None:
        """Disable a specific access right for a user.

        Parameters
        ----------
        user_id : int
            ID of the user whose access is being disabled.
        access_type : str
            Type of access to disable.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        date = datetime.datetime.now(TIMEZONE).date()
        try:
            query = """
            UPDATE access SET disabled_at = ? WHERE user_id = ? AND access_type = ?;
            """
            await conn.execute(query, (date, user_id, access_type))
            await conn.commit()
        finally:
            await conn.close()
