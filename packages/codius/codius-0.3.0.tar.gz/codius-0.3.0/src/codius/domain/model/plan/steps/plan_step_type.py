from enum import Enum


class PlanStepType(str, Enum):
    CREATE_FILE = "create_file"
    DELETE_FILE = "delete_file"
    DELETE_DIRECTORY = "delete_directory"
    MODIFY_FILE = "modify_file"

    @classmethod
    def is_destructive(cls, step_type: str) -> bool:
        return step_type in {cls.DELETE_FILE, cls.DELETE_DIRECTORY}
