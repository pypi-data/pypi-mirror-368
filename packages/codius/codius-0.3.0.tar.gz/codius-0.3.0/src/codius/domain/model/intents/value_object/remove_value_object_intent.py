from dataclasses import dataclass
from codius.domain.model.intents.intent_base import IntentBase
from codius.domain.model.intents.intent_type import IntentType
from codius.infrastructure.services.code_scanner.model.building_block_type import \
    BuildingBlockType


@dataclass
class RemoveValueObjectIntent(IntentBase):
    intent: IntentType = IntentType.REMOVE_VALUE_OBJECT
    building_block_type: BuildingBlockType = BuildingBlockType.VALUE_OBJECT
    target: str = ""

    @classmethod
    def to_example_json(cls) -> str:
        return """{
  "intent": "remove_value_object",
  "target": "Address"
}"""
