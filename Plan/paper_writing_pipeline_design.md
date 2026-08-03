# PaperPilot — Paper-Writing Pipeline: Design

## 1. Overview

**Goal:** given a folder of research artifacts (code, plots, results, notes, reference papers) and a target venue — or help picking one if the scholar hasn't decided — produce a submission-shaped LaTeX paper — properly structured, no blank/broken layout, naturally written, internally consistent — with minimal manual editing.

This is sub-project **D** of the overall PaperPilot decomposition (see `Plan_and_idea`). It assumes the research has already been evaluated as publishable (sub-project C) — this pipeline's job is turning already-good research into a well-formed paper, not judging whether the research is good.

**Non-goals:** no static knowledge base, no pre-built algorithm catalog, no AI-detector-evasion loop, no sandboxed code execution, no web frontend yet.

## 2. Architecture

An **MCP server**, not a standalone app with its own LLM billing. Claude (running inside Claude Code or Claude Desktop — host-agnostic) is the orchestrating agent: it reads the local files directly, drafts prose, does the style rewriting, and visually inspects rendered pages (native vision) to judge structural issues. Our code doesn't do the "thinking" — it exposes a small set of tools for the mechanical things Claude can't do itself (compiling LaTeX, rendering PDF pages to images, resolving/caching venue templates), and Claude decides when to call them and loops based on results.

The pipeline is structured around MCP's three primitives, though not in the
1:1 mapping originally assumed below (corrected after implementation, see the
note at the end of this section):

- **Tools** — mechanical operations (compiling LaTeX, rendering PDF pages,
  looking up/adding library templates) *and* the 5 pipeline-stage instruction
  sets (Screening, Venue Resolution, Structure/Drafting, Humanization, Final
  QA). Claude calls a stage's tool itself, mid-conversation, whenever it
  decides that stage is done and it's time for the next one.
- **Prompts** — exactly one: a human-invoked entry point (`write_paper`) that
  kicks off the whole pipeline. Everything after that first human action is
  Claude autonomously chaining through the 5 stage tools above.
- **Resources** (informal, not the MCP Resources primitive — see note) — the
  running pipeline state: screening report, structure-check results, style
  notes. Read/written via `read_resource`/`write_resource` tools rather than
  MCP's formal Resources primitive.

**Stage transitions**: at the end of a stage, Claude writes a compact handoff
summary of what it produced/decided via `write_resource` → the next stage's
tool is called, reading that summary back via `read_resource` as needed. This
keeps each phase's working context focused without relying on any
host-specific subagent mechanism (e.g. Claude Code's Task tool), so behavior
is identical on Claude Code or Desktop.

**Correction made after implementation (Task 11):** the original plan was to
register the 5 stage instruction sets as MCP *Prompts*, one per stage, on the
assumption that "Prompts" was simply the primitive for "a chunk of
instructions." That's wrong in a way that would have broken the whole
pipeline's autonomy: MCP Prompts are invoked by a *human* (e.g. a slash
command) — the model has no way to invoke one itself mid-conversation. Had
this shipped as designed, the user would have had to manually type 5 separate
slash commands and hand-copy text (like the domain summary) between them,
instead of Claude running the whole pipeline after one request. The fix:
the 5 stage instruction sets are Tools (which Claude *can* call on its own),
and there's a single human-invoked Prompt (`write_paper`) that starts the
pipeline and tells Claude to chain through the stage tools autonomously. The
same reasoning applies to `write_resource`/`read_resource`: they're callable
read+write functions, which don't fit MCP's Resources primitive either (that
primitive is for static, read-only, host-attached content) — they're Tools
too. In the end, only one thing in this whole server is a true MCP Prompt:
the single entry point that kicks everything off.

No API key of ours is involved anywhere — compute is billed to the user's own Claude session, not to us.

## 3. Pipeline Stages

### Stage 0 — Screening (pre-flight)

**Input:** everything in the local research folder (code, notebooks, images/plots, results files, notes/draft text, reference PDFs/links). Paper type and venue are **not** required yet — screening is venue-agnostic.

**Checks** (static/logical only, no code execution):
- Does the code's logic plausibly produce the claimed results?
- Are images/plots clear enough to be read and cited?
- Is there roughly enough substance here to write a paper at all? (a generic completeness check, independent of any specific venue's requirements — *not* the full novelty/publishability grading, which lives in sub-project C)

**Output:** a screening report, including a short summary of the work's topic/domain (used by venue recommendation in Stage 1). If gaps are found, the user is warned ("results may not meet expectations") but can choose to proceed anyway — this is a soft gate, never a hard block.

### Stage 1 — Paper type, venue selection & template resolution

**Paper type & venue capture** (happens after screening, since it doesn't need venue info):
- Ask the user for paper type: conference / journal / survey.
- Ask the user for the exact target venue (name or URL) — with an explicit **"not decided yet"** option.
- **If a venue is given** → proceed straight to template resolution below.
- **If undecided** → run venue recommendation: Claude searches the web (host's existing web-search tools, no scraper of our own) for upcoming conferences/journals of the chosen type whose call-for-papers deadline hasn't passed yet, matching the paper's topic/domain (from the Stage 0 screening summary). Rank purely on **scope/topic fit + open deadline** (v1 — no attempt to estimate competitiveness/acceptance-rate tiering) and present the **top 3** candidates with a one-line rationale each. User picks one, or supplies their own venue after seeing the suggestions.
- No new caching tool needed for this step — it's a live web-search reasoning task for Claude, same as the guideline lookup below, not a deterministic lookup.

**Template resolution** (once venue is known, either user-given or chosen from recommendations):
- Claude looks up the target venue's actual submission guidelines via web search (using the host's existing web-search/fetch tools — no scraper of our own).
- Calls `list_templates` and reasons over the metadata (publisher, format, applicable venues) to judge whether an existing library entry matches the venue's actual guidelines — a matching *judgment*, not an exact-string lookup, since venue names change yearly and would almost never match verbatim.
- If a match is found → `get_template_files` to retrieve it. If nothing matches → build a new template from the scraped guidelines (using a standard CTAN class where possible, so Tectonic can auto-fetch it, or a bespoke venue-specific style file when required) and call `add_template_to_library` so the same venue resolves instantly next time.
- The library is seeded with 6 common templates (IEEE conference/journal, ACM sigconf/journal, Springer LNCS, generic article) verified to compile via Tectonic's own auto-fetching of the underlying class file — no class file bytes need to be bundled for these. It lives locally at `~/.paperpilot/templates/<template_id>/`, growing organically for anything not already covered — never pre-built to be exhaustive.

### Stage 2 — Structure/Drafting

- Drafts the LaTeX paper from the best plots, graphs, results, and references, using the resolved template.
- Loop: `compile_latex` (wraps Tectonic) → parse compiler log for `Overfull`/`Underfull` box warnings (free, deterministic signal for overflow/collapsed tables) → `render_pdf_pages` (PyMuPDF) → Claude visually inspects each page image for blank regions, squeezed/overlapping tables, figure-text collisions, orphaned headings.
- Fixes are applied to the `.tex` source and the loop repeats until both signals are clean, capped at a maximum retry count (see Error Handling).

### Stage 3 — Humanization

- Paragraph-by-paragraph rewrite done directly by Claude for natural academic prose — no external humanizer/detector API, no AI-detection-evasion loop. Goal is writing quality, not concealment; venue AI-disclosure policy compliance is the scholar's responsibility as author of record.
- Followed by a correction pass: fix any broken LaTeX syntax or word-count drift the rewrite introduced, while staying consistent with the established style.

### Stage 4 — Final QA

- Checks the complete paper for internal consistency, hallucinated claims/citations, and fit to the target venue's guidelines.
- If an issue is found, it's routed back to whichever earlier stage owns it (structure issue → Stage 2, awkward phrasing → Stage 3) rather than restarting the whole pipeline.

**Output:** compiled PDF + `.tex` source + any supplementary files, written back into the local research folder as a submission package. Optional: one-click export of the project to the user's actual Overleaf account (via Overleaf's project-import mechanism) for continued manual editing — not part of the automated loop, just a convenience at the end.

## 4. MCP Tools (concrete)

- `compile_latex(project_dir) → { pdf_path, log_text, warnings[] }` — wraps Tectonic.
- `render_pdf_pages(pdf_path) → [image_path, ...]` — wraps PyMuPDF (`fitz`), one PNG per page. `cleanup_rendered_pages(pdf_path)` removes them once the structure loop finishes clean.
- `list_templates(paper_type?) → [metadata, ...]` — metadata for every template in the library (bundled seed + user-added), for Claude to match against a venue's actual guidelines.
- `get_template_files(template_id) → { filename: content, ... }` — retrieves a chosen template's files.
- `add_template_to_library(template_id, metadata, files) → confirmation` — persists a newly found/constructed template into the user's library (never touches the bundled seed data).

**Stack:** Python, using the official MCP Python SDK, Tectonic for compilation, PyMuPDF for rendering.

## 5. Error Handling & Edge Cases

- **Fatal compile errors** (not just warnings): Claude reads the error, fixes the source, retries — capped at a max retry count (e.g. 5) per stage before surfacing to the user for manual intervention instead of looping forever.
- **Venue guidelines not found anywhere on the web**: fall back to a generic default template (e.g. IEEE conference two-column) with an explicit warning to the user.
- **Final QA routing loop**: capped at a max number of round-trips (e.g. 3) between stages before stopping and reporting remaining issues to the user rather than looping indefinitely.
- **Screening failures**: always a soft warning, never a hard stop — user can proceed at their own discretion.

## 6. Testing/Validation

- **Tools** get real tests: a known-good `.tex` fixture compiles cleanly and produces expected warnings for a known-bad one; a sample PDF renders the expected number of page images.
- **Pipeline/prompts** get validated via end-to-end dry runs against a couple of small fixture research folders (sample code + plots + results + a fake target venue), checking that the stage sequence, handoff summaries, and routing logic behave as designed.

## 7. Explicitly Rejected Alternatives (and why)

- **Playwright automation of a real Overleaf account** for the compile loop — rejected: fragile against UI changes, slow per-iteration browser overhead, no official API for this, ToS gray area. Self-hosted Tectonic compilation used instead.
- **External AI-detector API (Winston, etc.) as a rewrite-loop stopping condition** — rejected: this makes detector-evasion the explicit design goal, which functions as concealing AI authorship from venues that require disclosure. Replaced with a style/quality-only rewrite loop with no detector in it.
- **Sandboxed code execution during screening** — rejected for now: static/logical read-through is faster, safer (no untrusted code execution), and works across any language/stack without building an execution sandbox.
