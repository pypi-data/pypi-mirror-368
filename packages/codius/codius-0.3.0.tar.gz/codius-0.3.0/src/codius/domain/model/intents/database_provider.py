from enum import Enum


class DatabaseProvider(str, Enum):
    POSTGRES = "Postgres"
    SQLITE = "SQLite"
