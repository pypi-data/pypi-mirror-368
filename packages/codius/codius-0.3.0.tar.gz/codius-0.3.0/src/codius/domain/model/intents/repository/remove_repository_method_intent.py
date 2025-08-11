from dataclasses import dataclass
from codius.domain.model.intents.intent_base import IntentBase
from codius.domain.model.intents.intent_type import IntentType
from codius.infrastructure.services.code_scanner.model.building_block_type import \
    BuildingBlockType


@dataclass
class RemoveRepositoryMethodIntent(IntentBase):
    intent: IntentType = IntentType.REMOVE_REPOSITORY_METHOD
    building_block_type: BuildingBlockType = BuildingBlockType.REPOSITORY
    target: str = ""
    method_name: str = ""

    @classmethod
    def to_example_json(cls) -> str:
        return """{
  "intent": "remove_repository_method",
  "target": "Person",
  "method_name": "FindByEmailAsync"
}"""
