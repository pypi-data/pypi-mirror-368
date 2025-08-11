from dataclasses import dataclass
from typing import Dict, Any

from codius.domain.model.plan.steps.plan_step_base import PlanStepBase
from codius.domain.model.plan.steps.plan_step_type import PlanStepType


@dataclass
class ModifyFileStep(PlanStepBase):
    modification: str
    context: Dict[str, Any]

    def __init__(self, path: str, description: str, modification: str, context: dict):
        super().__init__(type=PlanStepType.MODIFY_FILE, path=path, description=description)
        self.modification = modification
        self.context = context

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "modification": self.modification,
            "context": self.context
        })
        return base
