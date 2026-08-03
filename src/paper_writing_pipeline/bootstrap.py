"""One-time local setup for a fresh install: downloads cloudflared and
Tectonic if they aren't already present, and generates a persistent auth
token. Runs automatically before the server starts, so a fresh download
needs nothing manually configured beyond running the app once.

Downloads go through GitHub's Releases API and Cloudflare's stable
"latest" redirect -- never a third-party "curl a script and execute it"
URL, so there's always a specific, auditable artifact being fetched.
"""

import json
import secrets
import shutil
import urllib.request
import zipfile
from pathlib import Path

PAPERPILOT_DIR = Path.home() / ".paperpilot"
BIN_DIR = PAPERPILOT_DIR / "bin"
ENV_PATH = PAPERPILOT_DIR / ".env"

CLOUDFLARED_URL = (
    "https://github.com/cloudflare/cloudflared/releases/latest/download/"
    "cloudflared-windows-amd64.exe"
)
TECTONIC_RELEASES_API = "https://api.github.com/repos/tectonic-typesetting/tectonic/releases/latest"


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)


def ensure_cloudflared() -> Path:
    """Return the path to cloudflared.exe, downloading it if missing."""
    exe = BIN_DIR / "cloudflared.exe"
    if not exe.exists():
        _download(CLOUDFLARED_URL, exe)
    return exe


def ensure_tectonic() -> Path:
    """Return a path to tectonic.exe, downloading it if missing.

    Checks for an already-installed tectonic on PATH first, so a machine
    that already has it (e.g. installed manually, or via a package manager)
    doesn't get a second redundant copy.
    """
    exe = BIN_DIR / "tectonic.exe"
    if exe.exists():
        return exe

    on_path = shutil.which("tectonic")
    if on_path:
        return Path(on_path)

    with urllib.request.urlopen(TECTONIC_RELEASES_API) as response:
        release = json.load(response)
    asset_url = next(
        asset["browser_download_url"]
        for asset in release["assets"]
        if "windows-msvc" in asset["name"].lower()
    )

    zip_path = BIN_DIR / "tectonic-download.zip"
    _download(asset_url, zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(BIN_DIR)
    zip_path.unlink()
    return exe


def ensure_auth_token() -> str:
    """Return the persistent MCP_AUTH_TOKEN, generating one on first run."""
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if line.startswith("MCP_AUTH_TOKEN="):
                return line.split("=", 1)[1].strip()

    token = secrets.token_urlsafe(32)
    PAPERPILOT_DIR.mkdir(parents=True, exist_ok=True)
    with ENV_PATH.open("a", encoding="utf-8") as f:
        f.write(f"MCP_AUTH_TOKEN={token}\n")
    return token


def run_setup() -> dict:
    """Ensure everything a fresh install needs is present, fetching what's
    missing. Safe to call every startup -- each step is a no-op once its
    thing already exists."""
    return {
        "cloudflared_path": str(ensure_cloudflared()),
        "tectonic_path": str(ensure_tectonic()),
        "auth_token": ensure_auth_token(),
    }
