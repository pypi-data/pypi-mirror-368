import shutil

from pathlib import Path

from codius.infrastructure.services.project_metadata_service import ProjectMetadataService


def apply_changes(state: dict) -> dict:
    from codius.di import container

    metadata_service = container.resolve(ProjectMetadataService)

    session_id = state.get('session_id')
    generated_dir = metadata_service.get_generated_path(session_id)
    project_root = metadata_service.get_project_root()
    generated_files = list(generated_dir.rglob("*.cs"))

    # Copy generated files
    for src_path in generated_files:
        rel_path = src_path.relative_to(generated_dir)
        dest_path = project_root / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(src_path.read_text())

    # Handle deletions
    deleted_paths = []
    for plan_item in state.get("plan", []):
        if plan_item["type"] == "delete_directory":
            dir_path = project_root / plan_item["path"]
            if dir_path.exists() and dir_path.is_dir():
                shutil.rmtree(dir_path)
                deleted_paths.append(dir_path)
        elif plan_item["type"] == "delete_file":
            file_path = project_root / plan_item["path"]
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                deleted_paths.append(file_path)

    file_list = "\n".join([
        f"✅ {str(f.relative_to(generated_dir))}" for f in generated_files
    ] + [
        f"❌️ {str(p.relative_to(project_root))}" for p in deleted_paths
    ])

    state["final_output"] = f"Applied changes:\n\n{file_list}"
    return state
