from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from codius.infrastructure.services.code_scanner.model.building_block_type import \
    BuildingBlockType


@dataclass
class BuildingBlock:
    type: BuildingBlockType
    name: str
    file_path: Path
    namespace: Optional[str] = None
    properties: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "name": self.name,
            "file_path": str(self.file_path),
            "namespace": self.namespace,
            "properties": self.properties or [],
            "methods": self.methods or []
        }

    @staticmethod
    def from_dict(data: dict) -> "BuildingBlock":
        return BuildingBlock(
            type=BuildingBlockType(data["type"]),  # Deserialize back to enum
            name=data["name"],
            file_path=Path(data["file_path"]),
            namespace=data.get("namespace"),
            properties=data.get("properties", []),
            methods=data.get("methods", [])
        )
