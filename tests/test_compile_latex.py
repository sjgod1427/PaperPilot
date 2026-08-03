import pytest

from paper_writing_pipeline.tools.compile_latex import compile_latex

GOOD_TEX = r"""
\documentclass{article}
\begin{document}
hello world
\end{document}
"""

OVERFULL_TEX = r"""
\documentclass{article}
\begin{document}
\hbox to 1pt{This text is way too long to fit in a one point wide box and will overflow}
\end{document}
"""

FATAL_TEX = r"""
\documentclass{nonexistentclass923}
\begin{document}
hello
\end{document}
"""


def test_compile_latex_succeeds_with_no_warnings(tmp_path):
    (tmp_path / "main.tex").write_text(GOOD_TEX)

    result = compile_latex(str(tmp_path))

    assert result["pdf_path"] is not None
    assert (tmp_path / "main.pdf").exists()
    assert result["warnings"] == []


def test_compile_latex_reports_overfull_warning(tmp_path):
    (tmp_path / "main.tex").write_text(OVERFULL_TEX)

    result = compile_latex(str(tmp_path))

    assert result["pdf_path"] is not None
    assert any("Overfull" in warning for warning in result["warnings"])


def test_compile_latex_returns_no_pdf_path_on_fatal_error(tmp_path):
    (tmp_path / "main.tex").write_text(FATAL_TEX)

    result = compile_latex(str(tmp_path))

    assert result["pdf_path"] is None
    assert "error" in result["log_text"].lower()


def test_compile_latex_raises_when_main_tex_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        compile_latex(str(tmp_path))
