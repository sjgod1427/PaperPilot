import base64
import json
from pathlib import Path

SEED_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "seed_templates"
DEFAULT_USER_LIBRARY_DIR = Path.home() / ".paperpilot" / "templates"

# Files that exist alongside a template but aren't part of it: metadata is
# read separately, and reference PDFs are for human/Claude reading, never
# something to copy into a new paper project.
NON_TEMPLATE_FILES = {"metadata.json"}
REFERENCE_ONLY_EXTENSIONS = {".pdf"}

# Binary asset extensions get base64-encoded so they survive the dict[str, str]
# interface; everything else is read/written as plain text.
BINARY_ASSET_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".pdf"}


def _read_metadata(template_dir: Path) -> dict:
    return json.loads((template_dir / "metadata.json").read_text())


def _read_file_content(path: Path) -> str:
    if path.suffix.lower() in BINARY_ASSET_EXTENSIONS:
        return base64.b64encode(path.read_bytes()).decode("ascii")
    return path.read_text()


def _write_file_content(path: Path, content: str) -> None:
    if path.suffix.lower() in BINARY_ASSET_EXTENSIONS:
        path.write_bytes(base64.b64decode(content))
    else:
        path.write_text(content)


def _all_template_dirs(user_library_dir: Path) -> list[Path]:
    seed_dirs = [d for d in SEED_TEMPLATES_DIR.iterdir() if d.is_dir()]
    user_dirs = []
    if user_library_dir.exists():
        user_dirs = [d for d in user_library_dir.iterdir() if d.is_dir()]
    return seed_dirs + user_dirs


def list_templates(
    paper_type: str | None = None, user_library_dir: Path = DEFAULT_USER_LIBRARY_DIR
) -> list[dict]:
    """Return metadata for every template in the library (seed + user-added).

    Optionally filtered by paper_type ("conference", "journal", "survey").
    """
    metadata_entries = [
        _read_metadata(template_dir) for template_dir in _all_template_dirs(user_library_dir)
    ]
    if paper_type is None:
        return metadata_entries
    return [entry for entry in metadata_entries if entry["paper_type"] == paper_type]


def get_template_files(
    template_id: str, user_library_dir: Path = DEFAULT_USER_LIBRARY_DIR
) -> dict[str, str]:
    """Return {filename: content} for the files that belong in a new paper project.

    Excludes metadata.json and reference-only PDFs. Binary assets (images) are
    base64-encoded; everything else is plain text.
    """
    for template_dir in _all_template_dirs(user_library_dir):
        if _read_metadata(template_dir)["id"] == template_id:
            return {
                path.name: _read_file_content(path)
                for path in template_dir.iterdir()
                if path.name not in NON_TEMPLATE_FILES
                and path.suffix.lower() not in REFERENCE_ONLY_EXTENSIONS
            }
    raise FileNotFoundError(f"no template with id '{template_id}' in the library")


def add_template_to_library(
    template_id: str,
    metadata: dict,
    files: dict[str, str],
    user_library_dir: Path = DEFAULT_USER_LIBRARY_DIR,
) -> dict:
    """Add a new template to the user's library (never writes into the bundled seed dir).

    Always sets metadata["id"] to template_id, overriding whatever (if
    anything) the caller passed for "id" -- this is what get_template_files
    matches on, so a missing or mismatched "id" would silently make the
    template unreachable (or crash list_templates() entirely if "id" is
    missing), which happened for real once already.
    """
    template_dir = user_library_dir / template_id
    template_dir.mkdir(parents=True, exist_ok=True)
    metadata = {**metadata, "id": template_id}
    (template_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
    for filename, content in files.items():
        _write_file_content(template_dir / filename, content)
    return {"template_path": str(template_dir)}
