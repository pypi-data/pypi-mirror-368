from dataclasses import dataclass
from abc import ABC
from codius.domain.model.intents.intent_type import IntentType
from codius.infrastructure.services.code_scanner.model.building_block_type import \
    BuildingBlockType


@dataclass
class IntentBase(ABC):
    intent: IntentType
    building_block_type: BuildingBlockType

    def to_example_json(self) -> str:
        raise NotImplementedError("Subclasses must implement this method.")
