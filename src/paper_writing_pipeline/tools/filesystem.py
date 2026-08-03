import shutil
from pathlib import Path

from mcp.server.fastmcp import Image

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def read_file(path: str) -> str:
    """Read a text file at any local path on the machine this server runs on.

    For a client that has no local filesystem access of its own (e.g. a
    browser-based chat session reaching this server through a tunnel), this
    is how it reads research materials, main.tex, or anything else -- a
    client with its own file tools (Claude Code) can use those instead, but
    this must work the same way for clients that can't.
    """
    return Path(path).read_text(encoding="utf-8")


def write_file(path: str, content: str) -> None:
    """Write (creating or overwriting) a text file at any local path."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def list_directory(path: str) -> list[str]:
    """List every file under a directory, recursively, as absolute paths.

    Used to discover what's actually in a research folder without already
    knowing the file names -- directories themselves are not included, only
    files.
    """
    root = Path(path)
    return [str(p) for p in root.rglob("*") if p.is_file()]


def copy_file(source_path: str, dest_path: str) -> None:
    """Copy a file byte-for-byte -- for binary files (figures, PDFs) that
    read_file/write_file can't safely round-trip since they decode as UTF-8
    text. Use this to bring a figure from research_folder into project_dir
    so the paper references it with a relative path, not an absolute path
    pointing outside the project -- a real gap found in practice: without
    this, a paper compiled fine but only by \\includegraphics-ing a figure
    from its original external location, which isn't a self-contained
    submission package.
    """
    dest = Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(source_path, dest)


def read_image(path: str) -> Image:
    """Read an image file (a figure, or a rendered PDF page) so the calling
    client can actually see it, not just receive a path string.

    Only for genuine image files -- for a PDF page, call render_pdf_pages
    first to get PNG paths, then read those here.
    """
    suffix = Path(path).suffix.lower()
    if suffix not in IMAGE_EXTENSIONS:
        raise ValueError(f"'{path}' is not a supported image type ({IMAGE_EXTENSIONS})")
    return Image(path=path)
