# PaperPilot Website — Design Spec

## Goal

A marketing/distribution website for PaperPilot: explains what it is, hands
out the downloadable Windows installer, and walks a visitor through
connecting their own local instance to Claude Desktop, claude.ai (web), or
Claude Code — with interactive help (a setup wizard, OS-aware instructions,
a live connection checker) rather than a single static instructions page.

This site does **not** host or run PaperPilot itself. Every visitor's
PaperPilot instance runs on their own machine; the site only helps them get
there. This is a hard architectural constraint, not a preference — it's
what keeps user data private (never uploaded anywhere) and hosting cost at
zero (the site itself does no per-user compute).

## Tech stack

- **Next.js** (App Router), configured for static export (`output: 'export'`)
  — produces plain HTML/CSS/JS at build time, no Node server needed at
  runtime.
- **Tailwind CSS** + shadcn/ui component structure (`components/ui/`).
- **TypeScript** throughout.
- **Deployment:** GitHub Pages, same as the current static site — static
  export means no new hosting vendor is needed.
- **New dependencies:** `next`, `framer-motion`, `lucide-react`.
- **Location:** `website/` folder inside the existing PaperPilot repo,
  alongside the Python MCP server (`src/paper_writing_pipeline/`), kept as
  a clearly separate concern within the same project.

## Why not a plain static site (what we already had)?

The previous static HTML/CSS site (built earlier this session) covers the
pitch and instructions, but the user wants four things that need real
client-side app logic: OS-aware instructions, a live connection status
checker, an in-browser setup wizard, and a docs section that can grow over
time. None of these strictly require a server, so Next.js static export
gets the component/TypeScript ecosystem the user wants without giving up
free static hosting.

Two rejected alternatives, and why:
- **Full Next.js app on Vercel** — same capabilities, but a new hosting
  vendor for zero actual server-side need (nothing here requires SSR or API
  routes).
- **Vanilla JS bolted onto the existing static page** — no new hosting or
  vendor, but throws away the shadcn/Tailwind/TypeScript component
  ecosystem the user specifically asked for, and doesn't support React
  components (e.g. framer-motion-based ones) at all.

## Visual design — hero

Established and approved via live-rendered comparison during brainstorming
(not just described): a single approved direction, referred to as
"direction C" during design, combining:

- **Base identity:** dark near-black ground, a terminal-styled panel on one
  side showing a real, populated file tree from a research folder
  (`code/`, `data/`, `figures/`, `notes.md`) plus a live-looking pipeline
  status log (screening/venue/drafting marked done, humanization in
  progress with a blinking cursor), transforming via an arrow into a
  genuine two-column academic paper preview on the other side (white
  paper background, serif type, title/byline/abstract/section
  heading/justified two-column body text, page number — built to actually
  resemble a compiled LaTeX paper, not a generic content block).
- **Ambient treatment:** a bold version of the shooting-stars-grid
  aesthetic (dot-grid background, glow wash, animated twinkling stars,
  traveling light streaks) runs behind both panels — the terminal panel is
  semi-transparent/blurred (glassmorphic) so the ambient background
  visibly shows through it; the paper panel stays solid white/opaque since
  it represents an actual physical page.
- **Accent color:** cyan (`#67e8f9`), used for the emphasized headline
  phrase (with a layered white-glow text-shadow for a soft bloom effect),
  the arrow between panels, and the streak/star effects.
- **Typography:** monospace (JetBrains Mono or similar) for
  headings/terminal/labels; serif (Georgia or similar academic serif) only
  inside the paper-preview panel; system sans-serif for body copy
  elsewhere on the page.
- Full reference implementation from the brainstorming session is at
  `.superpowers/brainstorm/834-1785746240/content/hero-c-only.html` —
  use this as the literal starting point for the React hero component,
  not a re-interpretation from this written description.

Other sections of the page (privacy explainer, connection cards, wizard,
footer) reuse this same dark/cyan/mono visual language but weren't
individually mocked up live; standard application of the established
palette/type system during implementation.

## Pages & routing

- **`/` (home)** — hero → privacy explainer (with a small flow diagram:
  Claude → tunnel → PaperPilot → your files/Tectonic) → three connection-
  method cards (Desktop, web, Code) → inline setup wizard → download CTA →
  footer.
- **`/docs`** — growing docs section. Content lives as MDX files in
  `website/content/docs/*.mdx`; sidebar nav is generated from that file
  list, so adding a new doc page later requires no code changes. Seeded at
  launch with the current `INSTALL.md` content (setup steps +
  troubleshooting), split into individual doc pages.

## The four interactive features

### 1. OS auto-detection
Client-side only: read `navigator.userAgent` on mount, store a
`platform: 'windows' | 'mac' | 'linux' | 'unknown'` state. Drives which
platform's instructions/download button is shown by default. Per the
platform-scope decision made during brainstorming, only Windows has a real
download; Mac/Linux show "Coming soon" rather than a broken link, even
though detection correctly identifies them.

### 2. In-browser setup wizard
A client component, embedded on the home page (not a separate route), with
three steps:
1. Pick your Claude surface: Desktop/web vs. Claude Code.
2. Get the exact copy-paste commands for that surface (the `--stdio`
   registration command for Claude Code; download + connector-URL steps
   for Desktop/web).
3. Verify the connection — embeds feature #3 below as the final step.

### 3. Live connection status checker
The wizard cannot know a user's tunnel URL on its own — it's generated
locally by their own running `PaperPilot.exe` and only exists once they've
actually started it, so there is nothing for the wizard to carry over
automatically. The user must manually paste that URL into a text field.
Clicking "Check connection" does a client-side `fetch('<pasted-url>/health')`
and shows a status pill: checking (gray) / connected (green) / not
reachable (red).

**Required backend change** (Python side, not just the website): a new
route on PaperPilot's own server —

- `GET /health` → `{"status": "ok"}`, unauthenticated (no token required,
  since it reveals nothing sensitive), with CORS headers permitting the
  website's origin so the browser's cross-origin `fetch()` isn't blocked
  by the browser itself.
- This needs to be added to `main_remote()`'s Starlette app in
  `src/paper_writing_pipeline/server.py`, alongside the existing
  `BearerTokenMiddleware`.

### 4. Growing docs section
Standard Next.js MDX static content page as described under Pages above.
No dynamic behavior beyond normal client-side routing.

## Testing approach

- Normal component/build validation (`next build` succeeds, static export
  produces working output — verify by serving the `out/` directory
  locally before deploying).
- OS-detection logic spot-checked against a couple of representative
  user-agent strings (not exhaustive browser coverage).
- The one piece that needs to be validated for real, not just reasoned
  about: **run the actual `PaperPilot.exe`, expose it through a real
  cloudflared tunnel, and confirm the deployed (or local dev) site's
  `fetch()` to `<tunnel-url>/health` actually succeeds cross-origin** —
  CORS is a real, easy-to-get-wrong browser security mechanism, not
  something to assume works from reading the code.

## Explicitly out of scope for this spec

- Mac/Linux installers or packaging (website only *tailors messaging* for
  those platforms; building them is separate, larger, undecided work).
- Any server-side/hosted component of PaperPilot itself — the website
  never runs the pipeline, stores research data, or proxies MCP traffic.
- Redesigning sections other than the hero from scratch — they inherit the
  established palette/type system but weren't individually visually
  approved the way the hero was.
