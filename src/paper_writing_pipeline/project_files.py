from pathlib import Path


def write_project_file(project_dir: str, filename: str, content: str) -> None:
    """Create or fully overwrite a plain, user-visible file at the project root.

    Unlike write_resource (hidden internal handoff state under
    .pipeline_state/), this is for deliverables the scholar is meant to read
    directly, e.g. venue.md or approach.md.
    """
    path = Path(project_dir) / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def append_project_file(project_dir: str, filename: str, content: str) -> None:
    """Append to a plain, user-visible file at the project root, creating it if missing."""
    path = Path(project_dir) / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(content)


def read_project_file(project_dir: str, filename: str) -> str:
    """Read a plain, user-visible file previously written at the project root."""
    path = Path(project_dir) / filename
    if not path.exists():
        raise FileNotFoundError(f"no file '{filename}' found in {project_dir}")
    return path.read_text(encoding="utf-8")
