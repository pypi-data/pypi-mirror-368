from dataclasses import dataclass
from typing import List
from codius.domain.model.intents.intent_base import IntentBase
from codius.infrastructure.services.code_scanner.model.building_block_type import \
    BuildingBlockType


@dataclass(frozen=True)
class CompositeIntent:
    """
    Represents a group of granular intents that all apply to the same
    building block (e.g. an aggregate, repository, etc.).
    """
    target: str
    building_block_type: BuildingBlockType
    intents: List[IntentBase]
