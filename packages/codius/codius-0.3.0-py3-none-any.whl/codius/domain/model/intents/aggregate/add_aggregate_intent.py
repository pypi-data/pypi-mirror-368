from dataclasses import dataclass
from typing import List, Optional

from codius.domain.model.intents.intent_base import IntentBase
from codius.domain.model.intents.intent_type import IntentType
from codius.domain.model.intents.method import Method
from codius.domain.model.intents.property import Property
from codius.infrastructure.services.code_scanner.model.building_block_type import \
    BuildingBlockType


@dataclass
class AddAggregateIntent(IntentBase):
    intent: IntentType = IntentType.ADD_AGGREGATE
    building_block_type: BuildingBlockType = BuildingBlockType.AGGREGATE_ROOT
    target: str = ""
    properties: Optional[List[Property]] = None
    methods: Optional[List[Method]] = None

    @classmethod
    def to_example_json(cls) -> str:
        return """{
  "intent": "add_aggregate",
  "target": "Person",
  "properties": [
    { "name": "Id", "type": "Guid" },
    { "name": "Name", "type": "string" }
  ],
  "methods": [
    {
      "name": "Rename",
      "parameters": [
        { "name": "newName", "type": "string" }
      ]
    }
  ]
}"""
