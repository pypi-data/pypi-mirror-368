from dataclasses import dataclass
from codius.domain.model.intents.intent_base import IntentBase
from codius.domain.model.intents.intent_type import IntentType
from codius.domain.model.intents.property import Property
from codius.infrastructure.services.code_scanner.model.building_block_type import \
    BuildingBlockType


@dataclass
class AddAggregatePropertyIntent(IntentBase):
    intent: IntentType = IntentType.ADD_AGGREGATE_PROPERTY
    building_block_type: BuildingBlockType = BuildingBlockType.AGGREGATE_ROOT
    target: str = ""
    property: Property = None

    @classmethod
    def to_example_json(cls) -> str:
        return """{
  "intent": "add_aggregate_property",
  "target": "Person",
  "property": { "name": "Age", "type": "int" }
}"""
