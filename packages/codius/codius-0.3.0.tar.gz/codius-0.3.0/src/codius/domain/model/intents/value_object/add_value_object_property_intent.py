from dataclasses import dataclass
from codius.domain.model.intents.intent_base import IntentBase
from codius.domain.model.intents.intent_type import IntentType
from codius.domain.model.intents.property import Property
from codius.infrastructure.services.code_scanner.model.building_block_type import \
    BuildingBlockType


@dataclass
class AddValueObjectPropertyIntent(IntentBase):
    intent: IntentType = IntentType.ADD_VALUE_OBJECT_PROPERTY
    building_block_type: BuildingBlockType = BuildingBlockType.VALUE_OBJECT
    target: str = ""
    property: Property = None

    @classmethod
    def to_example_json(cls) -> str:
        return """{
  "intent": "add_value_object_property",
  "target": "Address",
  "property": { "name": "ZipCode", "type": "string" }
}"""
