import re
from pathlib import Path
from typing import List, Dict

from codius.infrastructure.services.code_scanner.model.building_block import BuildingBlock
from codius.infrastructure.services.code_scanner.model.building_block_type import BuildingBlockType


class BuildingBlockScanner:
    def scan(self, project_metadata: Dict) -> List[BuildingBlock]:
        return sorted(
            self._scan_domain_layer(project_metadata),
            key=lambda bb: (bb.type.value, bb.name)
        ) + sorted(
            self._scan_application_layer(project_metadata),
            key=lambda bb: (bb.type.value, bb.name)
        ) + sorted(
            self._scan_infrastructure_layer(project_metadata),
            key=lambda bb: (bb.type.value, bb.name)
        )

    def _scan_domain_layer(self, project_metadata: Dict) -> List[BuildingBlock]:
        domain_path = Path(project_metadata["domain_path"])
        return self._scan_files(domain_path, "domain")

    def _scan_application_layer(self, project_metadata: Dict) -> List[BuildingBlock]:
        application_path = Path(project_metadata["application_path"])
        return self._scan_files(application_path, "application")

    def _scan_infrastructure_layer(self, project_metadata: Dict) -> List[BuildingBlock]:
        infrastructure_path = Path(project_metadata["infrastructure_path"])
        return self._scan_files(infrastructure_path, "infrastructure")

    def _scan_files(self, base_path: Path, layer: str) -> List[BuildingBlock]:
        blocks = []

        for file_path in base_path.rglob("*.cs"):
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            class_name = file_path.stem

            if layer == "domain":
                if re.search(rf'\bclass\s+{class_name}\s*:\s*AggregateRootBase<', content):
                    blocks.append(self._create_block(BuildingBlockType.AGGREGATE_ROOT, class_name, file_path, content))
                elif re.search(rf'\bclass\s+{class_name}\s*:\s*EntityBase<', content):
                    blocks.append(self._create_block(BuildingBlockType.ENTITY, class_name, file_path, content))
                elif re.search(rf'\bclass\s+{class_name}\s*:\s*.*\bIValueObject\b', content):
                    blocks.append(self._create_block(BuildingBlockType.VALUE_OBJECT, class_name, file_path, content))
                elif re.search(rf'\bclass\s+{class_name}\s*:\s*.*\bIDomainEvent\b', content):
                    blocks.append(self._create_block(BuildingBlockType.DOMAIN_EVENT, class_name, file_path, content))
                elif re.search(r'\binterface\s+I\w+Repository\b', content):
                    blocks.append(self._create_block(BuildingBlockType.REPOSITORY, class_name, file_path, content))
                elif "IDomainService" in content:
                    blocks.append(self._create_block(BuildingBlockType.DOMAIN_SERVICE, class_name, file_path, content))
                elif "Ports" in str(file_path) and re.search(r'\binterface\s+I\w+\s*:\s*.*\bIPort\b', content):
                    blocks.append(self._create_block(BuildingBlockType.PORT, class_name, file_path, content))

            elif layer == "application":
                if re.search(rf'\bclass\s+{class_name}\s*:\s*.*\bIAction<', content):
                    blocks.append(self._create_block(BuildingBlockType.ACTION, class_name, file_path, content))
                elif re.search(rf'\bclass\s+{class_name}\s*:\s*.*\bICommand\b', content):
                    blocks.append(self._create_block(BuildingBlockType.COMMAND, class_name, file_path, content))
                elif "EventListenerBase" in content:
                    if class_name.endswith("IntegrationEventListener"):
                        blocks.append(self._create_block(BuildingBlockType.INTEGRATION_EVENT_LISTENER, class_name, file_path, content))
                    else:
                        blocks.append(self._create_block(BuildingBlockType.DOMAIN_EVENT_LISTENER, class_name, file_path, content))

            elif layer == "infrastructure":
                if "IInfrastructureService" in content:
                    blocks.append(self._create_block(BuildingBlockType.INFRASTRUCTURE_SERVICE, class_name, file_path, content))
                elif "Adapters" in str(file_path) and re.search(rf'\bclass\s+{class_name}\s*:\s*I\w+Port\b', content):
                    blocks.append(self._create_block(BuildingBlockType.ADAPTER, class_name, file_path, content))
                elif "ControllerBase" in content:
                    blocks.append(self._create_block(BuildingBlockType.ADAPTER, class_name, file_path, content))

        return blocks

    def _create_block(self, block_type: BuildingBlockType, name: str, file_path: Path, content: str) -> BuildingBlock:
        namespace_match = re.search(r'namespace\s+([\w\.]+)', content)
        namespace = namespace_match.group(1) if namespace_match else None

        properties = re.findall(r'public\s+\w+\s+(\w+)\s*\{', content)
        methods = re.findall(r'public\s+\w+\s+(\w+)\s*\([^)]*\)\s*\{', content)

        return BuildingBlock(
            type=block_type,
            name=name,
            file_path=file_path,
            namespace=namespace,
            properties=sorted(set(properties)),
            methods=sorted(set(methods)),
        )
