import logging

from pathlib import Path
from collections import defaultdict

from codius.domain.model.plan.steps.plan_step_type import PlanStepType
from codius.infrastructure.services.code_generator.code_generator_service import \
    CodeGeneratorService
from codius.infrastructure.services.project_metadata_service import ProjectMetadataService

logger = logging.getLogger(__name__)


def generate_code(state: dict) -> dict:
    from codius.di import container

    metadata_service = container.resolve(ProjectMetadataService)

    session_id = state.get('session_id')
    generated_dir = metadata_service.get_generated_path(session_id)
    output_dir = generated_dir
    project_root = Path(state["project_metadata"]["project_root"])
    plan = state.get("plan", [])

    code_generator = container.resolve(CodeGeneratorService)

    all_files = []
    created_files_map = {}

    modify_groups = defaultdict(list)
    create_steps = []

    for step in plan:
        if step["type"] == PlanStepType.CREATE_FILE:
            create_steps.append(step)
        elif step["type"] == PlanStepType.MODIFY_FILE:
            modify_groups[step["path"]].append(step)
        elif step["type"] == PlanStepType.DELETE_FILE or step["type"] == PlanStepType.DELETE_DIRECTORY:
            pass
        else:
            raise Exception(f"Unsupported plan step type: {step.get('type', '(none)')}")

    for step in create_steps:
        result = code_generator.create_file(step, output_dir, project_root)
        if result:
            all_files.append(result)
            created_files_map[step["path"]] = result["content"]

    for path, steps in modify_groups.items():
        result = code_generator.modify_file(
            path, steps, output_dir, project_root, created_files_map
        )
        if result:
            all_files = [f for f in all_files if f["path"] != result["path"]]
            all_files.append(result)

    state["generated_files"] = all_files
    return state
