import pytest

from paper_writing_pipeline.resources import read_resource, write_resource


def test_screening_report_round_trips(tmp_path):
    write_resource(str(tmp_path), "screening_report", "Code logic: warning. Plot clarity: pass.")

    assert read_resource(str(tmp_path), "screening_report") == (
        "Code logic: warning. Plot clarity: pass."
    )


def test_structure_check_results_round_trips(tmp_path):
    write_resource(str(tmp_path), "structure_check_results", "Fixed an overfull hbox on page 2.")

    assert read_resource(str(tmp_path), "structure_check_results") == (
        "Fixed an overfull hbox on page 2."
    )


def test_style_notes_round_trips(tmp_path):
    write_resource(str(tmp_path), "style_notes", "Prefers active voice, short paragraphs.")

    assert read_resource(str(tmp_path), "style_notes") == (
        "Prefers active voice, short paragraphs."
    )


def test_read_resource_raises_when_not_yet_written(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_resource(str(tmp_path), "screening_report")


def test_write_resource_overwrites_previous_content(tmp_path):
    write_resource(str(tmp_path), "style_notes", "first version")
    write_resource(str(tmp_path), "style_notes", "second version")

    assert read_resource(str(tmp_path), "style_notes") == "second version"
