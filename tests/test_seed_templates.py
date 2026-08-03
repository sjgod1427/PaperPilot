import base64
import tempfile
from pathlib import Path

import pytest

from paper_writing_pipeline.tools.compile_latex import compile_latex
from paper_writing_pipeline.tools.template_library import get_template_files, list_templates

# Use a fresh, guaranteed-empty directory instead of the real default
# (~/.paperpilot/templates/) so this regression test only ever covers the
# bundled seed templates -- never whatever a real user happens to have
# added to their own live library (which broke this test once already: a
# real add_template_to_library call saved an entry with a missing "id"
# field, which crashed list_templates() the next time this module loaded).
_EMPTY_USER_LIBRARY_DIR = Path(tempfile.mkdtemp())

SEED_TEMPLATE_IDS = [
    entry["id"] for entry in list_templates(user_library_dir=_EMPTY_USER_LIBRARY_DIR)
]


@pytest.mark.parametrize("template_id", SEED_TEMPLATE_IDS)
def test_seed_template_compiles_with_no_warnings(tmp_path, template_id):
    files = get_template_files(template_id, user_library_dir=_EMPTY_USER_LIBRARY_DIR)
    for filename, content in files.items():
        if filename.endswith(".png"):
            (tmp_path / filename).write_bytes(base64.b64decode(content))
        else:
            (tmp_path / filename).write_text(content)

    result = compile_latex(str(tmp_path))

    assert result["pdf_path"] is not None, result["log_text"]
    assert result["warnings"] == []
