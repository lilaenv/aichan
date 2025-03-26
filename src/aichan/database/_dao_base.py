import os
import re

from dotenv import load_dotenv

load_dotenv()


class SQLiteDaoBase:
    DB_NAME: str = os.environ["DB_NAME"]

    @staticmethod
    def validate_table_name(table_name: str) -> bool:
        """Only letters, numbers, and underscores are allowed."""
        pattern = r"^[A-Za-z0-9_]+$"
        return bool(re.match(pattern, table_name))
