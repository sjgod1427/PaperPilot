from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts.base import Prompt
from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route

from paper_writing_pipeline.bootstrap import run_setup
from paper_writing_pipeline.project_files import (
    append_project_file,
    read_project_file,
    write_project_file,
)
from paper_writing_pipeline.prompts.write_paper import write_paper_prompt
from paper_writing_pipeline.remote_auth import BearerTokenMiddleware
from paper_writing_pipeline.resources import read_resource, write_resource
from paper_writing_pipeline.stages.final_qa import final_qa_prompt
from paper_writing_pipeline.stages.humanization import humanization_prompt
from paper_writing_pipeline.stages.screening import screening_prompt
from paper_writing_pipeline.stages.structure_drafting import structure_drafting_prompt
from paper_writing_pipeline.stages.venue_resolution import venue_resolution_prompt
from paper_writing_pipeline.tools.compile_latex import compile_latex
from paper_writing_pipeline.tools.filesystem import (
    copy_file,
    list_directory,
    read_file,
    read_image,
    write_file,
)
from paper_writing_pipeline.tools.render_pdf import cleanup_rendered_pages, render_pdf_pages
from paper_writing_pipeline.tools.template_library import (
    add_template_to_library,
    get_template_files,
    list_templates,
)

# DNS-rebinding protection (the SDK's default Host-header allowlist) is
# disabled here because it can't know the tunnel's hostname, which changes
# every time a quick tunnel restarts. The bearer-token check in
# BearerTokenMiddleware is what actually gates access for the HTTP path
# below; it doesn't depend on the Host header, so it isn't weakened by this.
mcp = FastMCP(
    "paper-writing-pipeline",
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)

# The 5 stage-instruction functions are Tools, not Prompts: Claude needs to be
# able to call each one itself, mid-conversation, to chain autonomously from
# one stage to the next. MCP Prompts are invoked by a human (e.g. a slash
# command); Claude can't press that button on its own, which would force the
# user to manually invoke all 5 stages in sequence instead of one continuous
# pipeline run.
for tool_fn in (
    compile_latex,
    render_pdf_pages,
    cleanup_rendered_pages,
    read_file,
    write_file,
    list_directory,
    read_image,
    copy_file,
    list_templates,
    get_template_files,
    add_template_to_library,
    write_resource,
    read_resource,
    write_project_file,
    append_project_file,
    read_project_file,
    screening_prompt,
    venue_resolution_prompt,
    structure_drafting_prompt,
    humanization_prompt,
    final_qa_prompt,
):
    mcp.add_tool(tool_fn)

# write_paper_prompt is the one human-invoked entry point (e.g. a slash
# command) that kicks off the whole pipeline; everything after that is Claude
# chaining through the tools above on its own.
mcp.add_prompt(Prompt.from_function(write_paper_prompt))


def main() -> None:
    """Run over stdio -- for a local client that spawns this as a subprocess
    (Claude Code, Claude Desktop in local mode)."""
    mcp.run()


async def _health(request):
    return JSONResponse({"status": "ok"})


def build_remote_app(auth_token: str):
    """Build the Streamable HTTP app with auth and CORS, without starting a
    server -- split out from main_remote() so it's testable without spinning
    up uvicorn."""
    app = mcp.streamable_http_app()
    app.router.routes.append(Route("/health", _health, methods=["GET"]))
    app.add_middleware(BearerTokenMiddleware, expected_token=auth_token)
    # allow_origins=["*"] is deliberate: /health reveals nothing sensitive
    # (no auth token, no file contents, no project data), so there is no
    # security reason to restrict which site can check whether a PaperPilot
    # instance is reachable.
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"])
    return app


def main_remote() -> None:
    """Run over Streamable HTTP with bearer-token auth, bound to localhost only.

    For use behind a tunnel (Cloudflare/Tailscale/ngrok) so a cloud-hosted
    client (claude.ai, Claude Desktop's cloud mode) can reach this same local
    server. Every tool here can read/write files and run LaTeX compilation on
    this machine, so the auth token below is not optional once this is
    reachable from anywhere outside localhost.

    Calls run_setup() first, so a completely fresh install needs nothing
    manually configured -- cloudflared and Tectonic get downloaded and the
    auth token gets generated automatically on first run.
    """
    import uvicorn

    setup = run_setup()
    app = build_remote_app(setup["auth_token"])
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
