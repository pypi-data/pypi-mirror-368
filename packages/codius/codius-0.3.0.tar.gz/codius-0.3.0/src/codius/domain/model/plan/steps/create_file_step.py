from dataclasses import dataclass
from typing import Dict

from codius.domain.model.plan.steps.delete_file_step import PlanStepType
from codius.domain.model.plan.steps.plan_step_base import PlanStepBase


@dataclass
class CreateFileStep(PlanStepBase):
    template: str
    context: Dict[str, object]

    def __init__(self, path: str, description: str, template: str, context: dict):
        super().__init__(type=PlanStepType.CREATE_FILE, path=path, description=description)
        self.template = template
        self.context = context

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "template": self.template,
            "context": self.context
        })
        return base
