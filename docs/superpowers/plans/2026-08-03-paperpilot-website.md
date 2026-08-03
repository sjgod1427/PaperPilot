# PaperPilot Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the PaperPilot marketing/distribution website (Next.js, static export, shadcn/Tailwind/TypeScript) per `docs/superpowers/specs/2026-08-03-paperpilot-website-design.md`, plus the one required Python-side addition (`/health` endpoint).

**Architecture:** Next.js App Router site in `website/`, statically exported (`output: 'export'`) and deployable to GitHub Pages exactly like the current static site, but nothing gets pushed anywhere until the user explicitly says so. All four interactive features (OS detection, wizard, live connection checker, docs) run client-side; no server-side rendering or API routes are used.

**Tech Stack:** Next.js 15 (App Router), TypeScript, Tailwind CSS, shadcn/ui, framer-motion, lucide-react. Vitest for the one piece of pure logic (platform detection). Python side: Starlette (already a dependency), pytest.

---

## Prerequisite: Initialize git (do this before Task 0)

This directory is not yet a git repository. Every task below ends with a `git commit` step, so those steps fail without this. Per the standing instruction, this stays a **local-only** repository — nothing is pushed anywhere until explicitly told to.

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Initialize the repository**

Run: `git init`
Expected: `Initialized empty Git repository in .../PaperPilot/.git/`

- [ ] **Step 2: Create a `.gitignore`**

```
.venv/
__pycache__/
*.pyc
node_modules/
.next/
out/
dist/
build/
*.egg-info/
.pytest_cache/
```

- [ ] **Step 3: Initial commit**

```bash
git add .gitignore
git commit -m "chore: initialize repository"
```

- [ ] **Step 4: Commit existing project files**

```bash
git add -A
git commit -m "chore: snapshot existing PaperPilot project files"
```

Expected: commits succeed with no errors. Confirm with `git log --oneline` before moving to Task 0.

---

## Task 0: Add the `/health` endpoint to the Python server (do this first)

The website's connection checker depends on this existing before it can be meaningfully tested, so it goes first even though it's on the Python side.

**Files:**
- Modify: `src/paper_writing_pipeline/remote_auth.py`
- Modify: `src/paper_writing_pipeline/server.py`
- Test: `tests/test_health_endpoint.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_health_endpoint.py`:

```python
from starlette.testclient import TestClient

from paper_writing_pipeline.remote_auth import BearerTokenMiddleware
from paper_writing_pipeline.server import build_remote_app


def test_health_endpoint_requires_no_token():
    app = build_remote_app(auth_token="some-secret-token")
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_endpoint_has_cors_header():
    app = build_remote_app(auth_token="some-secret-token")
    client = TestClient(app)

    response = client.get("/health", headers={"Origin": "https://example.com"})

    assert response.headers.get("access-control-allow-origin") == "*"


def test_other_routes_still_require_token():
    app = build_remote_app(auth_token="some-secret-token")
    client = TestClient(app)

    response = client.post("/mcp", json={})

    assert response.status_code == 401
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_health_endpoint.py -v`
Expected: FAIL with `ImportError: cannot import name 'build_remote_app'` (it doesn't exist yet — `main_remote()` currently builds the app inline and never returns it, so there's nothing importable to test against).

- [ ] **Step 3: Add an `exempt_paths` option to `BearerTokenMiddleware`**

In `src/paper_writing_pipeline/remote_auth.py`, replace the existing class with:

```python
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
```

- [ ] **Step 4: Add the `/health` route and a `build_remote_app` factory**

In `src/paper_writing_pipeline/server.py`, add these imports near the top (alongside the existing ones):

```python
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route
```

Then add this function above `main_remote`, and replace `main_remote`'s body to use it:

```python
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
```

Remove the old inline app-building lines from `main_remote` (the `app = mcp.streamable_http_app()` / `app.add_middleware(...)` pair) since `build_remote_app` now does that.

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_health_endpoint.py -v`
Expected: PASS (3 passed)

- [ ] **Step 6: Run the full existing suite to confirm nothing broke**

Run: `uv run pytest -q`
Expected: all tests pass (28 total: 27 existing + 1 new file with 3 tests, i.e. 30 -- confirm the exact count in the actual output rather than assuming)

- [ ] **Step 7: Commit**

```bash
git add src/paper_writing_pipeline/remote_auth.py src/paper_writing_pipeline/server.py tests/test_health_endpoint.py
git commit -m "feat: add unauthenticated /health endpoint with CORS for the website's connection checker"
```

(Local commit only -- do not push, per the standing instruction to keep everything local until told otherwise.)

---

## Task 1: Scaffold the Next.js project

**Files:**
- Create: `website/` (entire project, via CLI)

- [ ] **Step 1: Run create-next-app**

From the PaperPilot repo root:

```bash
npx create-next-app@latest website --typescript --tailwind --app --no-src-dir --import-alias "@/*" --eslint
```

When prompted, accept defaults (App Router: yes, Turbopack: your choice, either works for this project).

- [ ] **Step 2: Verify the dev server starts**

Run: `cd website && npm run dev`
Expected: "Ready in ..." message, and `http://localhost:3000` shows the default Next.js starter page. Stop the server (Ctrl+C) once confirmed.

- [ ] **Step 3: Initialize shadcn/ui**

```bash
cd website
npx shadcn@latest init
```

Accept defaults (this creates `components.json`, `lib/utils.ts` with the `cn()` helper, and confirms the components path is `components/ui/`).

- [ ] **Step 4: Verify shadcn's default path is `components/ui/`**

Run: `cat components.json`
Expected: the `"aliases"` section shows `"ui": "@/components/ui"`. This matters because shadcn components (and our own custom components) need a single, predictable location -- if this were anything other than `components/ui/`, every future `npx shadcn add <component>` call would scatter files inconsistently and break the import aliases the rest of this plan assumes.

- [ ] **Step 5: Install the remaining dependencies**

```bash
npm install framer-motion lucide-react
```

- [ ] **Step 6: Commit**

```bash
git add website/
git commit -m "chore: scaffold Next.js website project with shadcn/Tailwind/TypeScript"
```

---

## Task 2: Configure static export

**Files:**
- Modify: `website/next.config.ts`

- [ ] **Step 1: Set static export mode**

Replace the contents of `website/next.config.ts` with:

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
```

(`images.unoptimized: true` is required alongside `output: "export"` -- Next.js's image optimization API needs a running server, which static export doesn't have.)

- [ ] **Step 2: Verify the build produces static output**

Run: `npm run build`
Expected: build succeeds, and a `website/out/` directory appears containing `index.html` and static assets.

- [ ] **Step 3: Verify the static output actually serves correctly**

Run: `npx serve out` (from inside `website/`)
Expected: prints a local URL (e.g. `http://localhost:3000`); opening it shows the same default Next.js page as the dev server. Stop the server once confirmed.

- [ ] **Step 4: Commit**

```bash
git add website/next.config.ts
git commit -m "chore: configure Next.js for static export"
```

---

## Task 3: Design tokens (color palette + type system) from the approved hero

**Files:**
- Modify: `website/app/globals.css`
- Reference: `.superpowers/brainstorm/834-1785746240/content/hero-c-only.html` (the approved live mockup -- copy these exact values from it, don't re-derive them)

- [ ] **Step 1: Add the color tokens as CSS custom properties**

Replace the `:root` block in `website/app/globals.css` (keep the rest of the Tailwind-generated file as-is) with:

```css
:root {
  --pp-bg: #07090f;
  --pp-bg-2: #0d1b2e;
  --pp-surface: #141b23;
  --pp-surface-2: #1b232d;
  --pp-border: #262f3a;
  --pp-ink: #e7e9ed;
  --pp-muted: #8b93a3;
  --pp-muted-2: #4d5665;
  --pp-accent: #67e8f9;
  --pp-accent-glow: rgba(103, 232, 249, 0.5);
  --pp-ok: #6ee7a0;
  --pp-paper: #ffffff;
  --pp-paper-border: #e5e2da;
  --pp-paper-ink: #2b2520;
  --pp-paper-muted: #6b6154;
  --pp-mono: ui-monospace, "SF Mono", Menlo, monospace;
  --pp-serif: Georgia, serif;
}
```

- [ ] **Step 2: Extend the Tailwind theme to expose these as utility classes**

In `website/app/globals.css`, inside the existing `@theme inline { ... }` block (Tailwind v4's CSS-based config -- if the scaffolded project uses a `tailwind.config.ts` instead, add an equivalent `extend.colors` block there), add:

```css
--color-pp-bg: var(--pp-bg);
--color-pp-bg-2: var(--pp-bg-2);
--color-pp-surface: var(--pp-surface);
--color-pp-surface-2: var(--pp-surface-2);
--color-pp-border: var(--pp-border);
--color-pp-ink: var(--pp-ink);
--color-pp-muted: var(--pp-muted);
--color-pp-muted-2: var(--pp-muted-2);
--color-pp-accent: var(--pp-accent);
--color-pp-ok: var(--pp-ok);
--color-pp-paper: var(--pp-paper);
--color-pp-paper-border: var(--pp-paper-border);
--color-pp-paper-ink: var(--pp-paper-ink);
--color-pp-paper-muted: var(--pp-paper-muted);
--font-pp-mono: var(--pp-mono);
--font-pp-serif: var(--pp-serif);
```

- [ ] **Step 3: Verify the tokens are usable**

Temporarily add `<div className="bg-pp-accent text-pp-bg p-4">token test</div>` to `website/app/page.tsx`, run `npm run dev`, confirm the div renders with a cyan background and near-black text at `http://localhost:3000`. Remove the test div afterward.

- [ ] **Step 4: Commit**

```bash
git add website/app/globals.css
git commit -m "feat: add PaperPilot design tokens (color palette + type system) from approved hero design"
```

---

## Task 4: Hero component

**Files:**
- Create: `website/components/hero.tsx`
- Reference: `.superpowers/brainstorm/834-1785746240/content/hero-c-only.html` -- port this exactly, do not re-interpret the design from the written spec description.

- [ ] **Step 1: Create the component**

Create `website/components/hero.tsx`. Port the full markup and animation behavior from the reference HTML file (terminal panel with the populated file tree and pipeline status log, arrow, paper preview panel with title/byline/rule/abstract/section heading/two-column justified body/page number, plus the grid background, glow wash, twinkling stars, and traveling light streaks). Use Tailwind utility classes driven by the tokens from Task 3 wherever practical; fall back to a scoped `<style jsx>` block (or a co-located CSS module, `hero.module.css`) for the parts that don't map cleanly to utilities (the CSS `@keyframes` for twinkle/shoot-h/shoot-v/blink, and the CSS-columns-based two-column paper text).

- [ ] **Step 2: Verify it renders identically to the approved reference**

Add `<Hero />` to `website/app/page.tsx` temporarily (replacing the default starter content), run `npm run dev`, open `http://localhost:3000`, and compare side-by-side against the reference file opened directly in a browser (`file:///.../hero-c-only.html` or via the still-running visual companion server if it's still up). Confirm: file tree content matches, status log shows the blinking cursor, paper panel shows real title/byline/abstract text, stars twinkle, streaks travel across the screen, and the terminal panel is visibly glassy/blurred against the moving background behind it.

- [ ] **Step 3: Verify reduced-motion is respected**

In your OS accessibility settings, enable "reduce motion" (or use browser devtools' "Emulate CSS prefers-reduced-motion: reduce"). Reload the page. Confirm the twinkle/shoot/blink animations stop or become static, per the artifact-design fundamentals this project has followed throughout (respect `prefers-reduced-motion`) -- add a `@media (prefers-reduced-motion: reduce)` block turning off the `animation` properties if this isn't already the case.

- [ ] **Step 4: Commit**

```bash
git add website/components/hero.tsx
git commit -m "feat: add Hero component (terminal-to-paper transformation, approved live-mockup design)"
```

---

## Task 5: Platform detection utility (with real unit tests)

**Files:**
- Create: `website/lib/platform-detect.ts`
- Test: `website/lib/platform-detect.test.ts`
- Modify: `website/package.json` (add Vitest)

- [ ] **Step 1: Add Vitest**

```bash
cd website
npm install -D vitest
```

Add to `website/package.json`'s `"scripts"`:

```json
"test": "vitest run"
```

- [ ] **Step 2: Write the failing test**

Create `website/lib/platform-detect.test.ts`:

```typescript
import { describe, expect, it } from "vitest";
import { detectPlatform } from "./platform-detect";

describe("detectPlatform", () => {
  it("detects Windows", () => {
    const ua =
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36";
    expect(detectPlatform(ua)).toBe("windows");
  });

  it("detects macOS", () => {
    const ua =
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15";
    expect(detectPlatform(ua)).toBe("mac");
  });

  it("detects Linux", () => {
    const ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36";
    expect(detectPlatform(ua)).toBe("linux");
  });

  it("falls back to unknown for anything else", () => {
    expect(detectPlatform("some unrecognized string")).toBe("unknown");
  });
});
```

- [ ] **Step 3: Run test to verify it fails**

Run: `npm run test`
Expected: FAIL with a module-not-found error for `./platform-detect`.

- [ ] **Step 4: Write the implementation**

Create `website/lib/platform-detect.ts`:

```typescript
export type Platform = "windows" | "mac" | "linux" | "unknown";

export function detectPlatform(userAgent: string): Platform {
  const ua = userAgent.toLowerCase();
  if (ua.includes("win")) return "windows";
  if (ua.includes("mac")) return "mac";
  if (ua.includes("linux") || ua.includes("x11")) return "linux";
  return "unknown";
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `npm run test`
Expected: PASS (4 tests)

- [ ] **Step 6: Add the client-side hook wrapping it**

Create `website/lib/use-platform.ts`:

```typescript
"use client";

import { useEffect, useState } from "react";
import { detectPlatform, type Platform } from "./platform-detect";

export function usePlatform(): Platform {
  const [platform, setPlatform] = useState<Platform>("unknown");

  useEffect(() => {
    setPlatform(detectPlatform(navigator.userAgent));
  }, []);

  return platform;
}
```

(The `useEffect` matters: `navigator` doesn't exist during Next.js's static/server render, so detection has to happen after the component mounts in the browser, not during the initial render pass.)

- [ ] **Step 7: Commit**

```bash
git add website/lib/platform-detect.ts website/lib/platform-detect.test.ts website/lib/use-platform.ts website/package.json
git commit -m "feat: add platform detection utility with unit tests"
```

---

## Task 6: Connection status checker component

**Files:**
- Create: `website/components/connection-checker.tsx`

- [ ] **Step 1: Write the component**

Create `website/components/connection-checker.tsx`:

```tsx
"use client";

import { useState } from "react";

type Status = "idle" | "checking" | "connected" | "unreachable";

export function ConnectionChecker() {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState<Status>("idle");

  async function checkConnection() {
    if (!url) return;
    setStatus("checking");
    try {
      const target = url.replace(/\/$/, "") + "/health";
      const response = await fetch(target, { method: "GET" });
      setStatus(response.ok ? "connected" : "unreachable");
    } catch {
      setStatus("unreachable");
    }
  }

  const statusLabel: Record<Status, string> = {
    idle: "Not checked yet",
    checking: "Checking...",
    connected: "Connected",
    unreachable: "Not reachable",
  };

  const statusColor: Record<Status, string> = {
    idle: "bg-pp-muted-2",
    checking: "bg-pp-muted",
    connected: "bg-pp-ok",
    unreachable: "bg-red-500",
  };

  return (
    <div className="flex flex-col gap-3">
      <label htmlFor="tunnel-url" className="text-sm text-pp-muted">
        Paste the URL PaperPilot printed (the part before <code>?token=</code> is fine too)
      </label>
      <div className="flex gap-2">
        <input
          id="tunnel-url"
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://your-tunnel.trycloudflare.com"
          className="flex-1 rounded-md border border-pp-border bg-pp-surface px-3 py-2 text-sm text-pp-ink"
        />
        <button
          onClick={checkConnection}
          disabled={!url || status === "checking"}
          className="rounded-md bg-pp-accent px-4 py-2 text-sm font-semibold text-pp-bg disabled:opacity-50"
        >
          Check connection
        </button>
      </div>
      <div className="flex items-center gap-2 text-sm">
        <span className={`h-2.5 w-2.5 rounded-full ${statusColor[status]}`} aria-hidden="true" />
        <span className="text-pp-muted">{statusLabel[status]}</span>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify it renders and handles a real success case**

This is the one piece the design spec calls out as needing real (not just code-reasoned) validation:

1. Run the real `PaperPilot.exe` (built earlier in this project) so it starts the tunnel and prints a URL.
2. Add `<ConnectionChecker />` temporarily to `website/app/page.tsx`, run `npm run dev`, open `http://localhost:3000`.
3. Paste the printed tunnel URL into the field and click "Check connection".
4. Expected: the status pill turns green and shows "Connected" -- confirming the `/health` endpoint (Task 0) and its CORS header actually work cross-origin from a real browser tab, not just in a Python test.
5. Also test the failure path: paste a garbage URL (e.g. `https://nonexistent.trycloudflare.com`) and confirm it shows red "Not reachable" rather than hanging or throwing an uncaught error.

- [ ] **Step 3: Commit**

```bash
git add website/components/connection-checker.tsx
git commit -m "feat: add live connection status checker component"
```

---

## Task 7: Setup wizard component

**Files:**
- Create: `website/components/setup-wizard.tsx`

- [ ] **Step 1: Write the component**

Create `website/components/setup-wizard.tsx`:

```tsx
"use client";

import { useState } from "react";
import { usePlatform } from "@/lib/use-platform";
import { ConnectionChecker } from "@/components/connection-checker";

type Surface = "desktop-web" | "claude-code";

export function SetupWizard() {
  const platform = usePlatform();
  const [step, setStep] = useState(1);
  const [surface, setSurface] = useState<Surface | null>(null);

  return (
    <div className="rounded-lg border border-pp-border bg-pp-surface p-6">
      <div className="mb-6 flex gap-2 font-pp-mono text-xs text-pp-muted">
        <span className={step === 1 ? "text-pp-accent" : ""}>1. Surface</span>
        <span>&rarr;</span>
        <span className={step === 2 ? "text-pp-accent" : ""}>2. Commands</span>
        <span>&rarr;</span>
        <span className={step === 3 ? "text-pp-accent" : ""}>3. Verify</span>
      </div>

      {step === 1 && (
        <div className="flex flex-col gap-3">
          <p className="text-pp-ink">Which do you use?</p>
          <button
            className="rounded-md border border-pp-border p-3 text-left hover:border-pp-accent"
            onClick={() => {
              setSurface("desktop-web");
              setStep(2);
            }}
          >
            Claude Desktop or claude.ai (web)
          </button>
          <button
            className="rounded-md border border-pp-border p-3 text-left hover:border-pp-accent"
            onClick={() => {
              setSurface("claude-code");
              setStep(2);
            }}
          >
            Claude Code
          </button>
        </div>
      )}

      {step === 2 && surface === "desktop-web" && (
        <div className="flex flex-col gap-3 font-pp-mono text-sm">
          <p className="font-sans text-pp-ink">
            {platform === "windows"
              ? "Double-click PaperPilot.exe."
              : "Run PaperPilot for your platform."}{" "}
            It prints a URL. Paste it into Settings &rarr; Connectors &rarr; Add custom connector.
          </p>
          <button
            onClick={() => setStep(3)}
            className="self-start rounded-md bg-pp-accent px-4 py-2 text-pp-bg"
          >
            Next: verify it worked
          </button>
        </div>
      )}

      {step === 2 && surface === "claude-code" && (
        <div className="flex flex-col gap-3">
          <pre className="overflow-x-auto rounded-md bg-pp-surface-2 p-3 font-pp-mono text-xs text-pp-ink">
            claude mcp add -s user paperpilot -- "C:\path\to\PaperPilot.exe" --stdio
          </pre>
          <p className="text-sm text-pp-muted">
            Start a fresh Claude Code session afterward -- it only checks for MCP servers at startup.
          </p>
          <button
            onClick={() => setStep(3)}
            className="self-start rounded-md bg-pp-accent px-4 py-2 text-pp-bg"
          >
            Done
          </button>
        </div>
      )}

      {step === 3 && surface === "desktop-web" && (
        <div className="flex flex-col gap-3">
          <p className="text-pp-ink">Paste the URL PaperPilot printed to confirm it's reachable:</p>
          <ConnectionChecker />
        </div>
      )}

      {step === 3 && surface === "claude-code" && (
        <p className="text-pp-ink">
          Claude Code connects directly, so there&apos;s no tunnel URL to verify here -- try
          asking Claude to use the <code>paperpilot</code> connector in a fresh session.
        </p>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verify all paths through the wizard manually**

Add `<SetupWizard />` to `website/app/page.tsx` temporarily, run `npm run dev`, and click through both branches (Desktop/web -> commands -> checker; Claude Code -> command -> done message). Confirm the step indicator highlights correctly at each stage and the `--stdio` command block is copy-pasteable (select the text, confirm no unwanted line wrapping breaks it).

- [ ] **Step 3: Commit**

```bash
git add website/components/setup-wizard.tsx
git commit -m "feat: add in-browser setup wizard component"
```

---

## Task 8: Privacy section, connection cards, nav, footer

**Files:**
- Create: `website/components/privacy-section.tsx`
- Create: `website/components/connection-cards.tsx`
- Create: `website/lib/constants.ts`
- Create: `website/components/nav.tsx`
- Create: `website/components/footer.tsx`

- [ ] **Step 1: Privacy section**

Create `website/components/privacy-section.tsx`:

```tsx
export function PrivacySection() {
  const flow = [
    "Claude",
    "private tunnel",
    "PaperPilot (your PC)",
    "your files · Tectonic",
  ];

  return (
    <section id="privacy" className="border-t border-pp-border py-16">
      <div className="mx-auto grid max-w-5xl grid-cols-1 gap-10 px-6 md:grid-cols-[1.1fr_0.9fr]">
        <div>
          <p className="mb-3 font-pp-mono text-xs uppercase tracking-wide text-pp-accent">
            Why it&apos;s built this way
          </p>
          <h2 className="mb-4 font-pp-mono text-2xl font-semibold text-pp-ink">
            Claude doesn&apos;t touch your files. PaperPilot does.
          </h2>
          <p className="mb-4 text-pp-muted">
            Claude Desktop and claude.ai run in the cloud &mdash; they have no way to reach a
            folder on your laptop. So instead of uploading your research anywhere, PaperPilot
            runs locally and opens a private tunnel just so Claude can <em>ask</em> it to do
            things. Every read, every LaTeX compile, every file write happens on your machine,
            under a token only you have.
          </p>
          <p className="text-pp-muted">
            <strong className="text-pp-ink">Claude Code</strong> skips the tunnel entirely
            &mdash; it already runs locally, so it talks to PaperPilot directly, no public URL
            involved at all.
          </p>
        </div>
        <div className="rounded-lg border border-pp-border bg-pp-surface p-6">
          {flow.map((node, i) => (
            <div key={node} className="flex items-center gap-3 py-2 font-pp-mono text-sm">
              {i > 0 && <span className="text-pp-muted-2">&rarr;</span>}
              <span
                className={`rounded-md border px-2.5 py-1 ${
                  i === 0
                    ? "border-pp-accent text-pp-accent"
                    : "border-pp-border bg-pp-surface-2 text-pp-ink"
                }`}
              >
                {node}
              </span>
            </div>
          ))}
          <p className="mt-4 font-pp-mono text-xs leading-relaxed text-pp-muted-2">
            Claude only ever sees what PaperPilot&apos;s tools return to it &mdash; never a
            direct line to your disk.
          </p>
        </div>
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Connection cards**

Create `website/components/connection-cards.tsx`:

```tsx
type Card = { title: string; body: string; tag: string };

const CARDS: Card[] = [
  {
    title: "Claude Desktop",
    body: "Double-click PaperPilot.exe. It opens a private tunnel and prints a URL — paste it into Settings → Connectors.",
    tag: "Remote connector",
  },
  {
    title: "claude.ai (web)",
    body: "Identical to Desktop — same exe, same tunnel, same URL. Add it as a custom connector in your browser.",
    tag: "Remote connector",
  },
  {
    title: "Claude Code",
    body: "Runs on your machine already, so no tunnel is created. Register the exe directly with --stdio.",
    tag: "Local, direct",
  },
];

export function ConnectionCards() {
  return (
    <section id="connect" className="border-t border-pp-border py-16">
      <div className="mx-auto max-w-5xl px-6">
        <p className="mb-3 font-pp-mono text-xs uppercase tracking-wide text-pp-accent">
          One download, three ways in
        </p>
        <h2 className="mb-8 font-pp-mono text-2xl font-semibold text-pp-ink">
          Connect it however you already use Claude
        </h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {CARDS.map((card) => (
            <div
              key={card.title}
              className="flex flex-col gap-3 rounded-lg border border-pp-border bg-pp-surface p-6"
            >
              <h3 className="font-pp-mono text-base text-pp-ink">{card.title}</h3>
              <p className="flex-1 text-sm text-pp-muted">{card.body}</p>
              <div className="border-t border-dashed border-pp-border pt-3 font-pp-mono text-xs uppercase tracking-wide text-pp-muted-2">
                {card.tag}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

- [ ] **Step 3: Nav and footer**

There is no real public GitHub URL for this project yet (nothing gets pushed
anywhere per the standing instruction), so both components import a single
placeholder constant instead of a guessed real-looking URL -- update this one
constant once a repository actually exists, rather than hunting through
multiple files.

Create `website/lib/constants.ts`:

```typescript
// TODO: replace with the real repository URL once one exists and the user
// has said it's OK to make this public. Do not fill this in with a guess.
export const GITHUB_URL = "#";
```

Create `website/components/nav.tsx`:

```tsx
import { GITHUB_URL } from "@/lib/constants";

export function Nav() {
  return (
    <nav className="flex items-center justify-between px-6 py-5">
      <div className="flex items-center gap-2.5 font-pp-mono text-sm font-semibold text-pp-ink">
        <span className="relative h-5 w-5 rounded border border-pp-accent">
          <span className="absolute inset-1 rounded-sm bg-pp-accent" />
        </span>
        PaperPilot
      </div>
      <div className="flex gap-7 font-pp-mono text-xs text-pp-muted">
        <a href="#privacy" className="hover:text-pp-ink">Privacy</a>
        <a href="#connect" className="hover:text-pp-ink">Connect</a>
        <a href="/docs/setup" className="hover:text-pp-ink">Docs</a>
        <a href={GITHUB_URL} className="hover:text-pp-ink">GitHub</a>
      </div>
    </nav>
  );
}
```

Create `website/components/footer.tsx`:

```tsx
import { GITHUB_URL } from "@/lib/constants";

export function Footer() {
  return (
    <footer className="flex flex-wrap items-center justify-between gap-3 px-6 py-10 font-pp-mono text-xs text-pp-muted-2">
      <span>PaperPilot &middot; runs locally &middot; MIT licensed</span>
      <a href={GITHUB_URL} className="text-pp-muted hover:text-pp-ink">
        Source on GitHub
      </a>
    </footer>
  );
}
```

- [ ] **Step 4: Verify visually**

Temporarily compose all four into `website/app/page.tsx` in order (Nav, Hero, PrivacySection, ConnectionCards), run `npm run dev`, and confirm each section renders with correct spacing and no broken layout at 375px, 768px, and 1440px widths (resize the browser or use devtools' device toolbar).

- [ ] **Step 5: Commit**

```bash
git add website/components/privacy-section.tsx website/components/connection-cards.tsx website/lib/constants.ts website/components/nav.tsx website/components/footer.tsx
git commit -m "feat: add privacy section, connection cards, nav, and footer components"
```

---

## Task 9: Docs section (MDX)

**Files:**
- Create: `website/content/docs/setup.mdx`
- Create: `website/content/docs/troubleshooting.mdx`
- Create: `website/app/docs/layout.tsx`
- Create: `website/app/docs/[slug]/page.tsx`
- Modify: `website/package.json` (MDX dependencies)

- [ ] **Step 1: Install MDX support**

```bash
cd website
npm install @next/mdx @mdx-js/loader @mdx-js/react @types/mdx gray-matter
```

- [ ] **Step 2: Port INSTALL.md content into doc pages**

Create `website/content/docs/setup.mdx` and `website/content/docs/troubleshooting.mdx`, splitting the existing repo-root `INSTALL.md` content between them (setup steps 1-4 into `setup.mdx`; the "Troubleshooting" and "Important things to know" sections into `troubleshooting.mdx`). Each file starts with frontmatter:

```mdx
---
title: Setup
order: 1
---

(content ported from INSTALL.md here)
```

- [ ] **Step 3: Build the docs layout and dynamic route**

Create `website/app/docs/layout.tsx` that reads all files in `content/docs/`, parses frontmatter with `gray-matter`, sorts by `order`, and renders a sidebar linking to each `/docs/<slug>`.

Create `website/app/docs/[slug]/page.tsx` using `generateStaticParams()` (required for static export with dynamic routes) to enumerate the same files and render the matched one's MDX content.

- [ ] **Step 4: Verify the docs pages build and render**

Run: `npm run build`
Expected: build succeeds and `website/out/docs/setup/index.html` and `website/out/docs/troubleshooting/index.html` both exist.

Run: `npx serve out` and open `/docs/setup` and `/docs/troubleshooting` in a browser -- confirm the sidebar lists both pages and content renders with the established dark styling (not default MDX black-on-white).

- [ ] **Step 5: Commit**

```bash
git add website/content/ website/app/docs/ website/package.json
git commit -m "feat: add docs section (MDX-driven, seeded from INSTALL.md)"
```

---

## Task 10: Assemble the home page

**Files:**
- Modify: `website/app/page.tsx`
- Modify: `website/app/layout.tsx`

- [ ] **Step 1: Compose the full home page**

Replace `website/app/page.tsx` with the full composition, in order: `Nav`, `Hero`, `PrivacySection`, `ConnectionCards`, `SetupWizard` (under a "Connect it however you already use Claude" heading), a download CTA band, `Footer`.

- [ ] **Step 2: Wire up the root layout**

Update `website/app/layout.tsx`'s metadata (`title`, `description`) to describe PaperPilot, and confirm the Plex/mono fonts (or whichever were chosen) are loaded via `next/font` rather than a CDN link (consistent with how fonts were embedded in every other artifact this project has produced).

- [ ] **Step 3: Full build verification**

Run: `npm run build && npx serve out`
Expected: home page loads at `/`, docs load at `/docs/setup` and `/docs/troubleshooting`, no console errors in the browser devtools.

- [ ] **Step 4: Re-run the full test suites**

Run: `npm run test` (Vitest, website) and `uv run pytest -q` (pytest, Python side)
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add website/app/page.tsx website/app/layout.tsx
git commit -m "feat: assemble full PaperPilot home page"
```

---

## Task 11: Real end-to-end verification (do not skip -- this is the one thing the design spec explicitly says can't just be reasoned about)

- [ ] **Step 1: Run the real stack together**

1. Run `PaperPilot.exe` (the actual packaged binary, not `uv run`) so it downloads/starts the tunnel and prints a real URL.
2. Run the website locally: `cd website && npm run build && npx serve out`.
3. Open the served site, go through the Setup Wizard's Desktop/web path end to end, paste the real printed URL into the connection checker at step 3.
4. Confirm it turns green ("Connected") -- this is the real cross-origin CORS behavior working, not a mock.

- [ ] **Step 2: Report back**

Stop here and report the result before doing anything else (e.g. deploying) -- per the standing instruction, nothing gets pushed anywhere until explicitly told to.
