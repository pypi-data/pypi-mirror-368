from typing import List
from codius.domain.model.plan.steps.create_file_step import CreateFileStep
from codius.domain.model.plan.steps.delete_file_step import DeleteFileStep
from codius.domain.model.plan.steps.modify_file_step import ModifyFileStep
from codius.domain.model.plan.steps.plan_step_base import PlanStepBase


class PlanExamples:
    @staticmethod
    def create_order_aggregate(root_prefix: str) -> CreateFileStep:
        return CreateFileStep(
            path=f"src/{root_prefix}/Domain/Model/Order/Order.cs",
            description="Create Order aggregate",
            template="domain/model/aggregate/aggregate_root",
            context={
                "aggregate_name": "Order",
                "namespace": f"{root_prefix}.Domain.Model.Order",
                "properties": [],
                "events": [],
                "commands": []
            }
        )

    @staticmethod
    def add_method_to_order(root_prefix: str) -> ModifyFileStep:
        return ModifyFileStep(
            path=f"src/{root_prefix}/Domain/Model/Order/Order.cs",
            description="Add SummarizeLines method to Order",
            modification="add_method",
            context={
                "aggregate_name": "Order",
                "method": {
                    "name": "SummarizeLines",
                    "parameters": [],
                    "returns": "OrderSummaryDto",
                    "body": "return new OrderSummaryDto(Lines.Count, Lines.Sum(l => l.Price));"
                },
                "placement": {
                    "type": "after_method",
                    "reference": "AddLine"
                }
            }
        )

    @staticmethod
    def delete_order_file(root_prefix: str) -> DeleteFileStep:
        return DeleteFileStep(
            path=f"src/{root_prefix}/Domain/Model/Order/Order.cs",
            description="Delete Order aggregate file"
        )

    @staticmethod
    def all(root_prefix: str) -> List[PlanStepBase]:
        return [
            PlanExamples.create_order_aggregate(root_prefix),
            PlanExamples.add_method_to_order(root_prefix),
            PlanExamples.delete_order_file(root_prefix),
        ]
