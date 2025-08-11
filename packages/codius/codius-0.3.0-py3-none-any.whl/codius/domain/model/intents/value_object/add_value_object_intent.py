from dataclasses import dataclass
from typing import List, Optional

from codius.domain.model.intents.intent_base import IntentBase
from codius.domain.model.intents.intent_type import IntentType
from codius.domain.model.intents.property import Property
from codius.infrastructure.services.code_scanner.model.building_block_type import \
    BuildingBlockType


@dataclass
class AddValueObjectIntent(IntentBase):
    intent: IntentType = IntentType.ADD_VALUE_OBJECT
    building_block_type: BuildingBlockType = BuildingBlockType.VALUE_OBJECT
    target: str = ""
    properties: Optional[List[Property]] = None

    @classmethod
    def to_example_json(cls) -> str:
        return """{
  "intent": "add_value_object",
  "target": "Address",
  "properties": [
    { "name": "Street", "type": "string" },
    { "name": "City", "type": "string" }
  ]
}"""
