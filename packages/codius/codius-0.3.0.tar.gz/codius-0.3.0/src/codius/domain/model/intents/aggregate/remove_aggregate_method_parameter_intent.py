from dataclasses import dataclass
from codius.domain.model.intents.intent_base import IntentBase
from codius.domain.model.intents.intent_type import IntentType
from codius.infrastructure.services.code_scanner.model.building_block_type import \
    BuildingBlockType


@dataclass
class RemoveAggregateMethodParameterIntent(IntentBase):
    intent: IntentType = IntentType.REMOVE_AGGREGATE_METHOD_PARAMETER
    building_block_type: BuildingBlockType = BuildingBlockType.AGGREGATE_ROOT
    target: str = ""
    method_name: str = ""
    parameter_name: str = ""

    @classmethod
    def to_example_json(cls) -> str:
        return """{
  "intent": "remove_aggregate_method_parameter",
  "target": "Person",
  "method_name": "Rename",
  "parameter_name": "newName"
}"""
