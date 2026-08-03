from pathlib import Path

import pymupdf

from paper_writing_pipeline.tools.render_pdf import cleanup_rendered_pages, render_pdf_pages


def _make_pdf(path: Path, page_count: int) -> None:
    doc = pymupdf.open()
    for _ in range(page_count):
        doc.new_page()
    doc.save(path)
    doc.close()


def test_render_pdf_pages_creates_one_image_per_page(tmp_path):
    pdf_path = tmp_path / "paper.pdf"
    _make_pdf(pdf_path, page_count=2)

    image_paths = render_pdf_pages(str(pdf_path))

    assert len(image_paths) == 2
    for image_path in image_paths:
        assert Path(image_path).exists()


def test_render_pdf_pages_clears_stale_pages_from_shorter_rerender(tmp_path):
    pdf_path = tmp_path / "paper.pdf"
    _make_pdf(pdf_path, page_count=3)
    render_pdf_pages(str(pdf_path))

    _make_pdf(pdf_path, page_count=1)
    image_paths = render_pdf_pages(str(pdf_path))

    pages_dir = tmp_path / "paper_pages"
    remaining_files = sorted(pages_dir.iterdir())

    assert len(image_paths) == 1
    assert len(remaining_files) == 1


def test_cleanup_rendered_pages_removes_the_folder(tmp_path):
    pdf_path = tmp_path / "paper.pdf"
    _make_pdf(pdf_path, page_count=1)
    render_pdf_pages(str(pdf_path))

    cleanup_rendered_pages(str(pdf_path))

    assert not (tmp_path / "paper_pages").exists()
