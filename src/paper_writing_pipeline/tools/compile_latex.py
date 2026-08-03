import re
import subprocess
from pathlib import Path

from paper_writing_pipeline.bootstrap import ensure_tectonic

WARNING_PATTERN = re.compile(r"^warning: .*(?:Overfull|Underfull).*$", re.MULTILINE)


def compile_latex(project_dir: str) -> dict:
    """Compile main.tex in project_dir with Tectonic.

    pdf_path is None if compilation failed to produce a PDF. log_text always
    contains the full compiler output so the caller can diagnose and fix the
    source before retrying.
    """
    entry_file = Path(project_dir) / "main.tex"
    if not entry_file.exists():
        raise FileNotFoundError(f"no main.tex found in {project_dir}")

    result = subprocess.run(
        [str(ensure_tectonic()), "main.tex"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    log_text = result.stdout + result.stderr
    warnings = WARNING_PATTERN.findall(log_text)

    pdf_path = str(Path(project_dir) / "main.pdf")
    if result.returncode != 0 or not Path(pdf_path).exists():
        pdf_path = None

    return {
        "pdf_path": pdf_path,
        "log_text": log_text,
        "warnings": warnings,
    }
