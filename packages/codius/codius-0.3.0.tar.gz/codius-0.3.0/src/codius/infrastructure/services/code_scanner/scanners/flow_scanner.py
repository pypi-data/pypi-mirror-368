import re
from typing import List, Optional, Set

from codius.infrastructure.services.code_scanner.model.building_block import BuildingBlock
from codius.infrastructure.services.code_scanner.model.building_block_type import BuildingBlockType


class FlowScanner:
    class Flow:
        def __init__(self, source: str, action: BuildingBlock, domain_logic: Optional[BuildingBlock], events: List[str]):
            self.source = source
            self.action = action
            self.domain_logic = domain_logic
            self.events = events

        def as_string(self) -> str:
            # Apply color based on source type
            if "listener" in self.source.lower():
                if "integration" in self.source.lower():
                    source_str = f"[bold bright_blue]{self.source}[/bold bright_blue]"
                else:
                    source_str = f"[bold blue]{self.source}[/bold blue]"
            else:
                source_str = f"[bold cyan]{self.source}[/bold cyan]"

            parts = [source_str, f"[green]{self.action.name}[/green]"]

            if self.domain_logic:
                parts.append(f"[yellow]{self.domain_logic.name}[/yellow]")

            for evt in self.events:
                parts.append(f"[magenta]{evt}[/magenta]")

            return " ➝ ".join(parts)

    def scan(self, building_blocks: List[BuildingBlock]) -> List["FlowScanner.Flow"]:
        adapters = [b for b in building_blocks if b.type == BuildingBlockType.ADAPTER and "Controller" in b.name]
        listeners = [b for b in building_blocks if "LISTENER" in b.type.name]
        actions = [b for b in building_blocks if b.type == BuildingBlockType.ACTION]

        flows: List[FlowScanner.Flow] = []

        for adapter in adapters:
            flows += self._scan_adapter_flows(adapter, actions, building_blocks)

        for listener in listeners:
            flows += self._scan_listener_flows(listener, actions, building_blocks)

        return flows

    def _scan_adapter_flows(
        self, adapter: BuildingBlock, actions: List[BuildingBlock], blocks: List[BuildingBlock]
    ) -> List["FlowScanner.Flow"]:
        flows = []
        try:
            content = adapter.file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return flows

        for action in actions:
            if re.search(rf'\b\w*{re.escape(action.name)}\b\s*\.\s*ExecuteAsync\(', content, re.IGNORECASE):
                domain_logic = self._find_called_block(action, blocks, {BuildingBlockType.AGGREGATE_ROOT, BuildingBlockType.DOMAIN_SERVICE})
                events = self._extract_published_events(domain_logic) if domain_logic else []
                flows.append(self.Flow(f"(webapi adapter) {adapter.name}", action, domain_logic, events))
        return flows

    def _scan_listener_flows(
        self, listener: BuildingBlock, actions: List[BuildingBlock],
        blocks: List[BuildingBlock]
    ) -> List["FlowScanner.Flow"]:
        flows = []

        try:
            content = listener.file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return flows

        # Try to find EventListenerBase<..., ActionName>
        match = re.search(r'EventListenerBase\s*<\s*\w+\s*,\s*(\w+)\s*>', content)
        if not match:
            return flows

        action_name = match.group(1)

        # Find matching action block by name
        action = next((a for a in actions if a.name == action_name), None)
        if not action:
            return flows

        domain_logic = self._find_called_block(action, blocks, {
            BuildingBlockType.AGGREGATE_ROOT, BuildingBlockType.DOMAIN_SERVICE
        })
        events = self._extract_published_events(domain_logic) if domain_logic else []

        label = "(domain event listener) " + listener.name
        if listener.name.endswith("IntegrationEventListener"):
            label = "(integration event listener) " + listener.name

        flows.append(self.Flow(label, action, domain_logic, events))
        return flows

    def _find_called_block(
        self, action: BuildingBlock, blocks: List[BuildingBlock], valid_types: Set[BuildingBlockType]
    ) -> Optional[BuildingBlock]:
        for bb in blocks:
            if bb.type in valid_types:
                for method in action.methods:
                    if bb.name.lower() in method.lower():
                        return bb
        return None

    def _extract_published_events(self, domain_logic_block: BuildingBlock) -> List[str]:
        try:
            content = domain_logic_block.file_path.read_text(encoding="utf-8", errors="ignore")
            # Heuristic: Look for `new EventName(...` in context of PublishAsync
            matches = re.findall(r'PublishAsync\s*\(\s*new\s+(\w+)\s*\(', content)
            return sorted(set(matches))
        except Exception:
            return []
