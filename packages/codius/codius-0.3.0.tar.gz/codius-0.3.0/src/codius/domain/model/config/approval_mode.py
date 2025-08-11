from enum import Enum


class ApprovalMode(str, Enum):
    SUGGEST = "suggest"
    AUTO = "auto"
