from dataclasses import dataclass
from typing import Optional

from codius.domain.model.intents.intent_base import IntentBase
from codius.domain.model.intents.intent_type import IntentType
from codius.domain.model.intents.persistence_provider import PersistenceProvider
from codius.domain.model.intents.database_provider import DatabaseProvider
from codius.infrastructure.services.code_scanner.model.building_block_type import \
    BuildingBlockType


@dataclass
class AddRepositoryIntent(IntentBase):
    intent: IntentType = IntentType.ADD_REPOSITORY
    building_block_type: BuildingBlockType = BuildingBlockType.REPOSITORY
    target: str = ""
    persistence_provider: Optional[PersistenceProvider] = None
    database_provider: Optional[DatabaseProvider] = None

    @classmethod
    def to_example_json(cls) -> str:
        return """{
  "intent": "add_repository",
  "target": "Person",
  "persistence_provider": "OpenDdd",
  "database_provider": "Postgres"
}"""
