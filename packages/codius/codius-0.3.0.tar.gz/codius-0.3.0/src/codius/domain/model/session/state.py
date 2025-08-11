from dataclasses import dataclass, field
from typing import Optional, List

from codius.infrastructure.services.code_scanner.model.building_block import BuildingBlock


@dataclass
class State:
    user_input: str = ""
    intent: Optional[dict] = None
    plan: Optional[dict] = None
    plan_warnings: List[str] = field(default_factory=list)
    generated_files: List[dict] = field(default_factory=list)
    final_output: Optional[str] = None
    status: str = "new"
    summary: Optional[str] = None
    project_metadata: Optional[dict] = None
    building_blocks: List[BuildingBlock] = field(default_factory=list)

    def clear_for_repl_cycle(self):
        self.user_input = ""
        self.intent = None
        self.plan = None
        self.plan_warnings.clear()
        self.generated_files.clear()
        self.final_output = None
        self.status = "?"

    def update_with_graph_result(self, result: dict):
        self.intent = result.get("intent")
        self.plan = result.get("plan")
        self.plan_warnings = result.get("plan_warnings", [])
        self.generated_files = result.get("generated_files", [])
        self.final_output = result.get("final_output")
        self.status = result.get("status", "completed")
        if "project_metadata" in result:
            self.project_metadata = result.get("project_metadata")
        if "building_blocks" in result:
            self.building_blocks = [
                BuildingBlock.from_dict(bb) for bb in result["building_blocks"]
            ]

    def summarize(self, summary: str):
        self.summary = summary
        self.user_input = ""
        self.intent = None
        self.plan = None
        self.plan_warnings.clear()
        self.generated_files.clear()
        self.final_output = None
        self.status = "compacted"

    def to_dict(self) -> dict:
        return {
            "user_input": self.user_input,
            "intent": self.intent,
            "plan": self.plan,
            "plan_warnings": self.plan_warnings,
            "generated_files": self.generated_files,
            "final_output": self.final_output,
            "status": self.status,
            "summary": self.summary,
            "project_metadata": self.project_metadata,
            "building_blocks": [
                bb.to_dict() if hasattr(bb, "to_dict") else bb
                for bb in self.building_blocks
            ]
        }

    @staticmethod
    def from_dict(data: dict) -> "State":
        return State(
            user_input=data.get("user_input", ""),
            intent=data.get("intent"),
            plan=data.get("plan"),
            plan_warnings=data.get("plan_warnings", []),
            generated_files=data.get("generated_files", []),
            final_output=data.get("final_output"),
            status=data.get("status", "new"),
            summary=data.get("summary"),
            project_metadata=data.get("project_metadata"),
            building_blocks=[
                BuildingBlock.from_dict(bb)
                for bb in data.get("building_blocks", [])
            ]
        )
