from pathlib import Path

STATE_DIR_NAME = ".pipeline_state"


def _state_path(project_dir: str, resource_name: str) -> Path:
    return Path(project_dir) / STATE_DIR_NAME / f"{resource_name}.md"


def write_resource(project_dir: str, resource_name: str, content: str) -> None:
    """Write a piece of pipeline handoff state (e.g. a screening report) for a project."""
    path = _state_path(project_dir, resource_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_resource(project_dir: str, resource_name: str) -> str:
    """Read a previously written piece of pipeline handoff state."""
    path = _state_path(project_dir, resource_name)
    if not path.exists():
        raise FileNotFoundError(f"no resource '{resource_name}' found for {project_dir}")
    return path.read_text(encoding="utf-8")
