import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

DEFAULT_EXEMPT_PATHS = frozenset({"/health"})


class BearerTokenMiddleware(BaseHTTPMiddleware):
    """Rejects any request that doesn't present the shared secret from MCP_AUTH_TOKEN.

    This is a single static shared secret, not real OAuth -- appropriate for a
    single personal deployment reached through a tunnel, not a multi-user
    public service. Every tool in this server can read/write files and run
    LaTeX compilation on this machine, so this check is not optional once the
    server is reachable over HTTP.

    Accepts the token either as a normal `Authorization: Bearer <token>`
    header (for clients that support custom headers, e.g. curl) or as a
    `?token=<token>` query parameter (for clients whose connector UI only
    lets you enter a URL, e.g. claude.ai's custom connector dialog, which has
    no field for a plain shared-secret header). The query-parameter path is a
    real trade-off: URLs can end up in browser history or logs in a way
    headers usually don't -- acceptable for a short-lived personal tunnel,
    not for anything longer-lived or multi-user.

    exempt_paths bypass the token check entirely -- only for routes that
    reveal nothing sensitive, like a bare liveness check.
    """

    def __init__(self, app, expected_token: str, exempt_paths=DEFAULT_EXEMPT_PATHS):
        super().__init__(app)
        self._expected_token = expected_token
        self._exempt_paths = exempt_paths

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self._exempt_paths:
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        provided = auth_header.removeprefix("Bearer ").strip() or request.query_params.get(
            "token", ""
        )
        if not provided or not secrets.compare_digest(provided, self._expected_token):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        return await call_next(request)
