from dataclasses import dataclass
from codius.domain.model.intents.intent_base import IntentBase
from codius.domain.model.intents.intent_type import IntentType
from codius.domain.model.intents.method import Method
from codius.infrastructure.services.code_scanner.model.building_block_type import \
    BuildingBlockType


@dataclass
class AddRepositoryMethodIntent(IntentBase):
    intent: IntentType = IntentType.ADD_REPOSITORY_METHOD
    building_block_type: BuildingBlockType = BuildingBlockType.REPOSITORY
    target: str = ""
    method: Method = None

    @classmethod
    def to_example_json(cls) -> str:
        return """{
  "intent": "add_repository_method",
  "target": "Person",
  "method": {
    "name": "FindByEmailAsync",
    "parameters": [
      { "name": "email", "type": "string" }
    ],
    "return_type": "IEnumerable<Person>",
    "is_async": true
  }
}"""
