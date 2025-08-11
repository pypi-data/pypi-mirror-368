from enum import Enum


class PersistenceProvider(str, Enum):
    OPEN_DDD = "OpenDDD"
    EF_CORE = "EFCore"
