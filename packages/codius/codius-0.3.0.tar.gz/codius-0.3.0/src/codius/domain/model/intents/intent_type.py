from enum import Enum

from codius.infrastructure.services.code_scanner.model.building_block_type import \
    BuildingBlockType


class IntentType(str, Enum):
    ADD_AGGREGATE = "add_aggregate"
    REMOVE_AGGREGATE = "remove_aggregate"
    ADD_AGGREGATE_PROPERTY = "add_aggregate_property"
    REMOVE_AGGREGATE_PROPERTY = "remove_aggregate_property"
    ADD_AGGREGATE_METHOD = "add_aggregate_method"
    REMOVE_AGGREGATE_METHOD = "remove_aggregate_method"
    ADD_AGGREGATE_METHOD_PARAMETER = "add_aggregate_method_parameter"
    REMOVE_AGGREGATE_METHOD_PARAMETER = "remove_aggregate_method_parameter"

    ADD_VALUE_OBJECT = "add_value_object"
    ADD_VALUE_OBJECT_PROPERTY = "add_value_object_property"
    REMOVE_VALUE_OBJECT = "remove_value_object"
    REMOVE_VALUE_OBJECT_PROPERTY = "remove_value_object_property"

    ADD_REPOSITORY = "add_repository"
    ADD_REPOSITORY_METHOD = "add_repository_method"
    REMOVE_REPOSITORY = "remove_repository"
    REMOVE_REPOSITORY_METHOD = "remove_repository_method"

    UNSURE = "unsure"

    @property
    def building_block(self) -> BuildingBlockType:
        if self.name.startswith("ADD_AGGREGATE") or self.name.startswith(
            "REMOVE_AGGREGATE"):
            return BuildingBlockType.AGGREGATE_ROOT
        elif self.name.startswith("ADD_VALUE_OBJECT") or self.name.startswith(
            "REMOVE_VALUE_OBJECT"):
            return BuildingBlockType.VALUE_OBJECT
        elif self.name.startswith("ADD_REPOSITORY") or self.name.startswith(
            "REMOVE_REPOSITORY"):
            return BuildingBlockType.REPOSITORY
        else:
            raise NotImplementedError(f"Building block not mapped for intent {self}")
