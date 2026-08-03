from pathlib import Path

import pymupdf

RENDER_DPI = 150


def _pages_dir(pdf_path: str) -> Path:
    pdf = Path(pdf_path)
    return pdf.with_name(f"{pdf.stem}_pages")


def render_pdf_pages(pdf_path: str) -> list[str]:
    """Render every page of pdf_path to a PNG, one file per page.

    Clears any previously rendered pages first so a shorter re-render
    never leaves stale pages behind from an earlier iteration.
    """
    output_dir = _pages_dir(pdf_path)
    if output_dir.exists():
        for old_file in output_dir.iterdir():
            old_file.unlink()
    else:
        output_dir.mkdir()

    image_paths = []
    with pymupdf.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            pixmap = page.get_pixmap(dpi=RENDER_DPI)
            image_path = output_dir / f"page-{page_number}.png"
            pixmap.save(image_path)
            image_paths.append(str(image_path))

    return image_paths


def cleanup_rendered_pages(pdf_path: str) -> None:
    """Remove the rendered page-image folder once it's no longer needed."""
    output_dir = _pages_dir(pdf_path)
    if not output_dir.exists():
        return
    for image_path in output_dir.iterdir():
        image_path.unlink()
    output_dir.rmdir()
