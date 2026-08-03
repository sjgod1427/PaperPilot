"""Single entry point for end users. With no arguments, runs the local
server and the tunnel together and prints the one URL + token to paste into
a remote connector (Claude Desktop or claude.ai web). With --stdio, instead
runs the plain stdio server -- no tunnel, no HTTP, no auth token -- for a
local client that spawns this as a subprocess directly (Claude Code, or
Claude Desktop's local-server mode), the same way `claude mcp add` would
invoke `uv run paper-writing-pipeline` in a source checkout. One downloaded
.exe covers both cases instead of needing two separate builds.
"""

import re
import subprocess
import sys
import threading
import time

from paper_writing_pipeline.bootstrap import run_setup

SERVER_PORT = 8000
TUNNEL_URL_PATTERN = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
TUNNEL_STARTUP_TIMEOUT_SECONDS = 30


def _print(message: str = "") -> None:
    # Python buffers stdout when it isn't attached to a real terminal (e.g.
    # inside a packaged .exe's console window in some launch modes), so a
    # plain print() can silently never reach the screen. Every status
    # message the user actually needs to see goes through this instead.
    print(message, flush=True)


def _run_server(auth_token: str) -> None:
    import uvicorn

    from paper_writing_pipeline.remote_auth import BearerTokenMiddleware
    from paper_writing_pipeline.server import mcp

    app = mcp.streamable_http_app()
    app.add_middleware(BearerTokenMiddleware, expected_token=auth_token)
    uvicorn.run(app, host="127.0.0.1", port=SERVER_PORT, log_level="warning")


def _start_tunnel(cloudflared_path: str) -> tuple[subprocess.Popen, str]:
    """Launch cloudflared and block until its public URL appears in its
    output, or raise if it doesn't show up within the timeout."""
    process = subprocess.Popen(
        [cloudflared_path, "tunnel", "--url", f"http://localhost:{SERVER_PORT}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    deadline = time.monotonic() + TUNNEL_STARTUP_TIMEOUT_SECONDS
    for line in process.stdout:
        match = TUNNEL_URL_PATTERN.search(line)
        if match:
            return process, match.group(0)
        if time.monotonic() > deadline:
            break

    process.terminate()
    raise RuntimeError(
        f"cloudflared didn't report a tunnel URL within {TUNNEL_STARTUP_TIMEOUT_SECONDS}s"
    )


def main() -> None:
    if "--stdio" in sys.argv:
        from paper_writing_pipeline.server import main as run_stdio_server

        run_stdio_server()
        return

    _print("Setting up PaperPilot (downloading anything missing on first run)...")
    setup = run_setup()

    server_thread = threading.Thread(
        target=_run_server, args=(setup["auth_token"],), daemon=True
    )
    server_thread.start()
    time.sleep(1)  # give uvicorn a moment to bind the port before the tunnel needs it

    _print("Starting your private tunnel...")
    tunnel_process, tunnel_url = _start_tunnel(setup["cloudflared_path"])
    connector_url = f"{tunnel_url}/mcp?token={setup['auth_token']}"

    _print()
    _print("=" * 70)
    _print("PaperPilot is ready.")
    _print()
    _print("For Claude Desktop or claude.ai (web):")
    _print("Paste this URL into Claude's connector settings:")
    _print(f"  {connector_url}")
    _print()
    _print("Using Claude Code instead? Close this and see the Claude Code")
    _print("section of INSTALL.md -- it doesn't need this URL or tunnel at all.")
    _print()
    _print("Keep this window open -- closing it stops PaperPilot.")
    _print("Press Ctrl+C to stop.")
    _print("=" * 70)

    try:
        tunnel_process.wait()
    except KeyboardInterrupt:
        pass
    finally:
        tunnel_process.terminate()
        sys.exit(0)


if __name__ == "__main__":
    main()
