import base64

import pytest

from paper_writing_pipeline.tools.template_library import (
    add_template_to_library,
    get_template_files,
    list_templates,
)

SEED_TEMPLATE_IDS = {
    "ieee-conference",
    "ieee-transactions-journal",
    "acm-sigconf",
    "acm-journal",
    "springer-lncs",
    "generic-article",
}


def test_list_templates_returns_all_seed_templates(tmp_path):
    entries = list_templates(user_library_dir=tmp_path)

    assert {entry["id"] for entry in entries} == SEED_TEMPLATE_IDS


def test_list_templates_filters_by_paper_type(tmp_path):
    entries = list_templates(paper_type="journal", user_library_dir=tmp_path)

    assert {entry["id"] for entry in entries} == {
        "ieee-transactions-journal",
        "acm-journal",
    }


def test_get_template_files_excludes_metadata_json(tmp_path):
    files = get_template_files("ieee-conference", user_library_dir=tmp_path)

    assert "metadata.json" not in files
    assert "main.tex" in files
    assert "IEEEtran" in files["main.tex"]


def test_get_template_files_raises_for_unknown_id(tmp_path):
    with pytest.raises(FileNotFoundError):
        get_template_files("not-a-real-template", user_library_dir=tmp_path)


def test_get_template_files_excludes_reference_pdf(tmp_path):
    files = get_template_files("ieee-conference", user_library_dir=tmp_path)

    assert "IEEE_Conference_Template.pdf" not in files


def test_get_template_files_base64_encodes_binary_assets(tmp_path):
    files = get_template_files("ieee-conference", user_library_dir=tmp_path)

    assert "fig1.png" in files
    decoded = base64.b64decode(files["fig1.png"])
    assert decoded.startswith(b"\x89PNG")


def test_add_template_to_library_round_trips_binary_assets(tmp_path):
    original_bytes = b"\x89PNG\r\n\x1a\nfake png data"
    add_template_to_library(
        "with-image",
        {
            "id": "with-image",
            "publisher": "test",
            "paper_type": "conference",
            "format": "single-column",
            "class_name": "article",
            "documentclass_invocation": "\\documentclass{article}",
            "applicable_to": "test",
            "notes": "test",
        },
        {"logo.png": base64.b64encode(original_bytes).decode("ascii")},
        user_library_dir=tmp_path,
    )

    files = get_template_files("with-image", user_library_dir=tmp_path)

    assert base64.b64decode(files["logo.png"]) == original_bytes


def test_add_template_to_library_is_findable_afterward(tmp_path):
    add_template_to_library(
        "neurips",
        {
            "id": "neurips",
            "publisher": "NeurIPS",
            "paper_type": "conference",
            "format": "single-column",
            "class_name": "article",
            "documentclass_invocation": "\\documentclass{article}",
            "applicable_to": "NeurIPS conference submissions.",
            "notes": "Requires the current year's neurips_20XX.sty from the official site.",
        },
        {"main.tex": "\\documentclass{article}", "neurips_2026.sty": "% style file contents"},
        user_library_dir=tmp_path,
    )

    entries = list_templates(user_library_dir=tmp_path)
    files = get_template_files("neurips", user_library_dir=tmp_path)

    assert "neurips" in {entry["id"] for entry in entries}
    assert files["neurips_2026.sty"] == "% style file contents"


def test_add_template_to_library_does_not_touch_seed_dir(tmp_path):
    add_template_to_library(
        "temp-test-template",
        {
            "id": "temp-test-template",
            "publisher": "test",
            "paper_type": "conference",
            "format": "single-column",
            "class_name": "article",
            "documentclass_invocation": "\\documentclass{article}",
            "applicable_to": "test",
            "notes": "test",
        },
        {"main.tex": "\\documentclass{article}"},
        user_library_dir=tmp_path,
    )

    entries_with_addition = {entry["id"] for entry in list_templates(user_library_dir=tmp_path)}
    entries_without_addition = {
        entry["id"] for entry in list_templates(user_library_dir=tmp_path.parent / "unused")
    }

    assert "temp-test-template" in entries_with_addition
    assert "temp-test-template" not in entries_without_addition
