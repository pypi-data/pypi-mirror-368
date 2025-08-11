from dataclasses import dataclass
from codius.domain.model.intents.intent_base import IntentBase
from codius.domain.model.intents.intent_type import IntentType
from codius.domain.model.intents.parameter import Parameter
from codius.infrastructure.services.code_scanner.model.building_block_type import \
    BuildingBlockType


@dataclass
class AddAggregateMethodParameterIntent(IntentBase):
    intent: IntentType = IntentType.ADD_AGGREGATE_METHOD_PARAMETER
    building_block_type: BuildingBlockType = BuildingBlockType.AGGREGATE_ROOT
    target: str = ""
    method_name: str = ""
    parameter: Parameter = None

    @classmethod
    def to_example_json(cls) -> str:
        return """{
  "intent": "add_aggregate_method_parameter",
  "target": "Person",
  "method_name": "Rename",
  "parameter": { "name": "newName", "type": "string" }
}"""
