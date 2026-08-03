# Paper-Writing Pipeline Implementation Plan

**Goal:** build the MCP server described in `paper_writing_pipeline_design.md` — tools for LaTeX compilation, PDF page rendering, and venue template caching, plus the prompts/resources that structure the 5-stage pipeline.

**Architecture:** Python MCP server. Claude (via Claude Code or Claude Desktop) does all the reasoning/drafting/vision-checking; our code only provides mechanical tools it can't do itself.

**Tech stack:** Python, official MCP Python SDK, Tectonic (LaTeX compilation), PyMuPDF (`fitz`, PDF→image rendering).

**How this plan differs from the standard format:** per your ground rules, this plan defines file structure, build order, and interfaces only — no code is pre-written here. For each task below, when we reach it, I'll present the viable implementation approaches for that specific file, you pick or redirect, then we write it together. No task is committed to git automatically; we commit only when you ask, with no AI-attribution trailer.

---

## File Structure

New project folder, sibling to `Plan/` at the PaperPilot root (not nested inside `Plan/`, which stays docs-only): `paper_writing_pipeline/`

```
PaperPilot/
  Plan/                          # docs only
  pyproject.toml                 # uv project root (not nested — see Task 1 note)
  src/paper_writing_pipeline/
    server.py                    # MCP server entrypoint — registers 13 tools + 1 prompt
    tools/
      render_pdf.py              # render_pdf_pages, cleanup_rendered_pages
      compile_latex.py           # compile_latex
      template_library.py        # list_templates, get_template_files, add_template_to_library
    seed_templates/               # 6 seeded templates + helper.txt diagnostic playbook
    stages/                        # the 5 pipeline-stage instruction sets — registered as Tools,
      screening.py                 # not Prompts, so Claude can chain through them on its own
      venue_resolution.py
      structure_drafting.py
      humanization.py
      final_qa.py
    prompts/                       # the one true MCP Prompt: human-invoked entry point
      write_paper.py
    resources.py                   # pipeline state (screening report, structure-check results, style notes)
  tests/
    test_render_pdf.py
    test_compile_latex.py
    test_template_library.py
    test_seed_templates.py
    test_resources.py
```

Note: this tree reflects the final structure. Two corrections happened along the way, both noted in their respective tasks below: the project root moved from a nested `paper_writing_pipeline/` folder to the `PaperPilot/` root (Task 1), and the `prompts/` folder split into `stages/` (Tools) + `prompts/` (the one real Prompt) after a registration bug was caught post-Task 11.

Each tool file has one job. Stage instruction sets are separated per stage (in `stages/`) so each is independently editable without touching the others. `resources.py` centralizes how pipeline state is stored/retrieved between stages — the one piece every stage touches, so it stays in its own file rather than duplicated per stage.

## Build Order & Task Breakdown

Bottom-up: shared tools first (nothing else works without them), then the prompts that use them, in pipeline order.

### Task 1: Project scaffolding
**Files:** `pyproject.toml`, `src/paper_writing_pipeline/server.py`, `src/paper_writing_pipeline/__init__.py`
**Responsibility:** a minimal MCP server that starts up, connects over stdio, and exposes zero tools yet — just proves the server boots and a host (Claude Code/Desktop) can attach to it.
**Verify:** server starts without error; host can list its (empty) tool set.

### Task 2: `render_pdf_pages` tool
**Files:** `src/paper_writing_pipeline/tools/render_pdf.py`, `tests/test_render_pdf.py`
**Interface:**
- `render_pdf_pages(pdf_path: str) -> list[str]` — renders each page to a PNG in a sibling `<pdf_stem>_pages/` folder, overwriting on each call (clears stale pages first, so a shorter re-render doesn't leave old page files behind).
- `cleanup_rendered_pages(pdf_path: str) -> None` — deletes the `_pages/` folder once the Structure/Drafting loop (Task 7) finishes clean, so only the final PDF remains.
**Responsibility:** wraps PyMuPDF page rasterization at 150 DPI. Simplest tool, no external binary dependency — good first real tool.
**Verify:** generates a small PDF on the fly with PyMuPDF (no committed binary fixture needed); asserts correct page count, stale-page clearing on re-render, and cleanup removes the folder.

### Task 3: `compile_latex` tool
**Files:** `src/paper_writing_pipeline/tools/compile_latex.py`, `tests/test_compile_latex.py`
**Interface:** `compile_latex(project_dir: str) -> dict` — runs `tectonic main.tex` in `project_dir` (fixed entry filename — the Structure/Drafting agent always names its draft `main.tex`, no auto-detection needed). Returns `{pdf_path: str | None, log_text: str, warnings: list[str]}`. `pdf_path` is `None` on fatal compile failure (non-zero exit / no PDF produced) so the caller can branch on it directly. `warnings` is parsed from stderr (Tectonic writes `Overfull`/`Underfull` diagnostics there; progress notes go to stdout).
**Responsibility:** wraps the Tectonic CLI (installed via direct GitHub release binary, placed in `~/.local/bin` — Chocolatey install failed on this machine due to non-elevated shell) and its warning output.
**Verify:** 4 tests — clean compile (no warnings), an intentionally overfull `\hbox` (warning captured), a fatal error via a missing document class (`pdf_path is None`), and a missing `main.tex` (raises `FileNotFoundError`).

### Task 4: Template library tools
**Files:** `src/paper_writing_pipeline/tools/template_library.py`, `tests/test_template_library.py`, seed data in `src/paper_writing_pipeline/seed_templates/<template_id>/{metadata.json,main.tex}`.
**Interface:**
- `list_templates(paper_type: str | None = None, user_library_dir: Path = DEFAULT_USER_LIBRARY_DIR) -> list[dict]` — returns metadata for every template (bundled seed + user-added), optionally filtered by paper_type.
- `get_template_files(template_id: str, user_library_dir: Path = DEFAULT_USER_LIBRARY_DIR) -> dict[str, str]` — returns `{filename: content}` for a chosen template. Excludes `metadata.json` and reference-only PDFs; binary assets (images) are base64-encoded, everything else is plain text.
- `add_template_to_library(template_id: str, metadata: dict, files: dict[str, str], user_library_dir: Path = DEFAULT_USER_LIBRARY_DIR) -> dict` — adds a new template to the user's library (never writes into the bundled seed dir).
**Responsibility:** replaces the original exact-match venue-name cache design (rejected — venue names change yearly, so exact match almost never hits). This is a **template library** matched by format/metadata reasoning (Claude's job, comparing a venue's actual guidelines against the metadata list) rather than a mechanical string lookup. Seeded with 6 templates verified to compile via Tectonic (auto-fetches the class file itself, so only metadata + a skeleton `main.tex` need to be bundled — no class file bytes): `ieee-conference`, `ieee-transactions-journal`, `acm-sigconf`, `acm-journal`, `springer-lncs`, `generic-article`. Venue-specific styles not on CTAN (NeurIPS, ICML, etc.) are deliberately **not** seeded — Claude fetches the current year's real file from the web the first time a scholar targets one, then calls `add_template_to_library` to grow the library organically. All 6 templates were upgraded from bare skeletons to richly structured documents (multi-author block, table, figure, references, and format-specific front matter like ACM's copyright block or IEEE's biography sections) since a bare skeleton gives Claude nothing to structurally learn from and the vision-based structure checker (Task 7) needs a realistic multi-element document to be tested against meaningfully. Each has a `fig1.png` placeholder figure generated with PyMuPDF.
**Verify:** 22 tests total for this task's area — 9 in `test_template_library.py` (all seed templates present, paper_type filtering, file retrieval excludes metadata.json and reference PDFs, unknown id raises, binary assets round-trip via base64, a newly added template is findable afterward, adding never touches the seed dir) plus 6 in `test_seed_templates.py` (parametrized regression test that actually compiles every seed template via Tectonic and asserts zero warnings, so a future edit that breaks one is caught automatically).

### Task 5: Screening prompt — DONE
**Files:** `src/paper_writing_pipeline/stages/screening.py`
**Interface:** `screening_prompt(research_folder: str) -> str` — plain function (undecorated, matching Tasks 2-4's pattern; MCP `@mcp.prompt()` registration happens in Task 11's wire-up). Takes `research_folder` as an explicit argument rather than inferring it from context, so a host surfacing this as a slash-command prompts the user for the path directly.
**Responsibility:** instructs Claude to read the research folder and produce a screening report (code-logic plausibility, image clarity, rough completeness) plus a topic/domain summary — per design Stage 0. No tool calls needed here beyond file reads the host already provides.
**Verify:** manual dry run — built a small fixture folder (a script with a real train/test-leakage bug, a results file with the resulting misleading number, and a deliberately illegible tiny plot image) and followed the prompt's instructions directly. It correctly surfaced all three issues (the leakage bug, the illegible plot, thin overall content) plus a usable domain summary, confirming the prompt produces a genuinely useful report rather than just well-formed text.

### Task 6: Venue Resolution prompt — DONE
**Files:** `src/paper_writing_pipeline/stages/venue_resolution.py`
**Interface:** `venue_resolution_prompt(domain_summary: str) -> str` — plain function (same undecorated pattern as Task 5), takes the Stage 0 domain summary as an explicit argument rather than assuming it's already in context, so this stage is self-contained and testable without Task 10 (resources.py) existing yet.
**Responsibility:** instructs Claude to ask paper type + venue (with "not decided" option), and on "not decided," search the web for upcoming venues matching type + domain summary, rank by scope fit + open deadline, present top 3. Then resolve the template via `list_templates`/`get_template_files`/`add_template_to_library`, falling back to the `generic-article` template with a warning if no guidelines can be found anywhere on the web.
**Verify:** manual dry run — confirmed the function renders correctly, then validated Step 3's matching logic against a real venue via an actual web search (IEEE ICRA 2026): its real guidelines ("standard IEEE conference LaTeX template, two-column, IEEEtran") match the `ieee-conference` seed entry's metadata exactly, confirming the reasoning-based match (not exact-string) works correctly against real-world data.

### Task 7: Structure/Drafting prompt — DONE
**Files:** `src/paper_writing_pipeline/stages/structure_drafting.py`
**Interface:** `structure_drafting_prompt(project_dir: str, template_id: str, research_folder: str, max_retries: int = 5) -> str` — plain function, same pattern as Tasks 5-6.
**Responsibility:** instructs Claude to draft the `.tex` from the resolved template + research materials, then loop `compile_latex` → check warnings → `render_pdf_pages` → vision-inspect → fix, until clean or `max_retries` is hit (stop and report to the user rather than looping forever), then `cleanup_rendered_pages`. Per your instruction, the blank-space diagnostic guidance is both inlined directly in the prompt (`KEY_LESSONS` constant, guaranteed visibility) *and* references `helper.txt` by path for the full playbook — and Step 6 explicitly instructs Claude to append newly discovered fixes back to `helper.txt`, so the playbook keeps growing across future runs.
**Verify:** manual dry run — built a fixture with a deliberately unbreakable ~90-character token causing a ~230pt Overfull \\hbox. Followed the prompt's own fix-order guidance literally: microtype (no effect on such a large overflow) → `\\emergencystretch` (still didn't close it) → reword (fixed it) — confirming the guidance's fix ordering is correct and the loop converges well within the retry cap. Appended this exact finding to `helper.txt` as a new diagnostic tell (large overfull + no natural break points → skip straight to rewording).

### Task 8: Humanization prompt — DONE
**Files:** `src/paper_writing_pipeline/stages/humanization.py`
**Interface:** `humanization_prompt(project_dir: str, max_retries: int = 3) -> str` — same undecorated-function pattern as Tasks 5-7. Smaller default retry cap than Stage 2 (3 vs. 5) since this stage is only catching rewrite-introduced regressions, not fixing structure from scratch.
**Responsibility:** instructs Claude to rewrite paragraph-by-paragraph for natural prose (preserving every technical claim/number/citation exactly, flagging paragraphs whose length changes drastically as a sign of dropped/padded content), then reuses `compile_latex` to verify the rewrite didn't break LaTeX syntax, fixing and retrying up to `max_retries` times. No detector API anywhere — per the design's explicitly-rejected-alternatives section.
**Verify:** manual before/after read-through — rewrote a deliberately robotic test paragraph ("It is important to note that... Furthermore... Moreover... In conclusion...") into natural prose, confirmed all 5 original claims survived with no additions, then built a fixture and actually ran `compile_latex` on the rewritten paragraph to confirm Step 2's verification mechanism works (compiled cleanly, zero warnings).

### Task 9: Final QA prompt — DONE
**Files:** `src/paper_writing_pipeline/stages/final_qa.py`
**Interface:** `final_qa_prompt(project_dir: str, venue_name: str, max_roundtrips: int = 3) -> str` — same undecorated-function pattern as Tasks 5-8.
**Responsibility:** instructs Claude to check internal consistency, hallucinated claims/citations, and venue fit across the whole paper. Issues are fixed inline using the same technique the owning stage would use (structural → Stage 2's compile+render+fix loop; prose → Stage 3's rewrite+recompile; consistency/hallucination → direct correction + recompile) rather than literally re-invoking `structure_drafting_prompt`/`humanization_prompt`, since those assume a full draft/rewrite pass and would be wrong for a single targeted fix. Re-checks all three items after any fix, capped at `max_roundtrips`.
**Verify:** manual dry run — built a fixture with a planted inconsistency (abstract claimed a 25-point hit-rate improvement; the results table showed 0.41→0.57, actually 16 points). Followed the prompt myself: caught the mismatch, corrected the abstract's number, recompiled — which surfaced a small unrelated Overfull \\hbox, correctly routed to Stage 2's technique (microtype) since it's a structural issue, not a consistency one. Resolved both issues in 2 round-trips, under the cap of 3.

**Update after the first real live run (via an actual Claude Code MCP connection, not a hand-built fixture):** the hallucination check missed a real issue — invented methodological specifics (a source that only said "12-layer image classifier, evaluated on a 10,000-image held-out test set" turned into a paper claiming CIFAR-10, 32x32 images, 3x3 convolutions with batch norm and ReLU, single-CPU-core measurement, batch size 1 — none of it stated anywhere in the source). Every individual invented detail was plausible, the paper compiled clean, and general skepticism wasn't enough to catch it. Fixed by rewriting item 2 of `final_qa_prompt` to explicitly require cross-checking every concrete noun/number/technical detail in Method/Setup/Experiments against the source material line by line, not just checking that citations are real. Documented as a new entry in `helper.txt` with the real example, since this is exactly the kind of thing worth a played-back concrete case rather than an abstract rule.

The same live run also surfaced two other real bugs, fixed immediately: (1) `add_template_to_library` didn't enforce that `metadata["id"]` matches the `template_id` argument — the live run saved a real template (`iclr-2026`, to the user's actual `~/.paperpilot/templates/`) with no `"id"` field at all, which crashed `list_templates()` on every subsequent call; fixed by having `add_template_to_library` always inject `metadata["id"] = template_id`, and patched the already-broken real entry directly. (2) `tests/test_seed_templates.py` called `list_templates()` with no `user_library_dir` override, so it silently scanned the real user's home-directory library instead of just the bundled seeds — meaning a real user's library growing via actual usage could break the test suite, which is exactly what happened. Fixed by pointing the test at a dedicated empty temp directory instead.

### Task 10: Resources (pipeline state) — DONE
**Files:** `src/paper_writing_pipeline/resources.py`, `tests/test_resources.py`
**Interface:** `write_resource(project_dir: str, resource_name: str, content: str) -> None` / `read_resource(project_dir: str, resource_name: str) -> str` — one generic pair rather than 6 near-duplicate named functions, since all three resource types (screening report, structure-check results, style notes) are handled identically (plain text stored per project). Files live at `{project_dir}/.pipeline_state/{resource_name}.md`, kept separate from the paper's actual LaTeX source so they never accidentally get swept into compilation or a submission package. `read_resource` raises `FileNotFoundError` if nothing's been written yet, matching `compile_latex`'s established pattern for a missing `main.tex`. The current `.tex` draft itself needs no wrapper here -- it's just `project_dir/main.tex`, already a real file every stage reads directly.
**Verify:** 5 tests — round-trip for each of the three resource types, reading before any write raises `FileNotFoundError`, and writing twice overwrites rather than appending.

### Task 11: Wire-up & end-to-end dry run — DONE (revised after a real registration bug)
**Files:** `src/paper_writing_pipeline/server.py` (modified), `src/paper_writing_pipeline/prompts/write_paper.py` (new)
**Responsibility:** registers 13 tools and exactly 1 prompt. The 8 mechanical tools (`compile_latex`, `render_pdf_pages`, `cleanup_rendered_pages`, `list_templates`, `get_template_files`, `add_template_to_library`, `write_resource`, `read_resource`) plus, after the correction below, the 5 stage-instruction functions (`screening_prompt`, `venue_resolution_prompt`, `structure_drafting_prompt`, `humanization_prompt`, `final_qa_prompt`) are all registered as Tools via `mcp.add_tool(fn)`. The single Prompt is a new function, `write_paper_prompt(research_folder, project_dir)`, registered via `mcp.add_prompt(Prompt.from_function(fn))` — the one human-invoked entry point that kicks off the whole pipeline.

**Bug caught and fixed after initial wire-up:** the 5 stage functions were originally registered as MCP Prompts (matching the design doc's original "one Prompt per stage" framing). This was wrong in a way that would have broken the pipeline's autonomy: MCP Prompts are invoked by a *human* (e.g. a slash command) — the model cannot invoke one itself mid-conversation. As designed, the user would have had to manually type 5 separate slash commands and hand-copy handoff text (like the domain summary) between them, rather than Claude running straight through all 5 stages after one request. Fixed by moving all 5 to Tools (which Claude *can* call on its own) and adding the single `write_paper` Prompt as the one human-triggered starting point. Also reconfirmed `write_resource`/`read_resource` belong as Tools, not the formal MCP Resources primitive (host-attached, static, URI-addressable — confirmed by `add_resource`'s actual signature, which takes a static `Resource` object, not a callable).
**Verify:** confirmed via `list_tools()`/`list_prompts()` that the server exposes exactly 13 tools and 1 prompt (`write_paper_prompt`) after the fix above. The end-to-end dry run below was run by calling the underlying functions directly (same behavior either way, since registration type doesn't change what a function does when called) before the Prompt-vs-Tool bug was caught; its conclusions still hold --
  - **Screening**: caught nothing wrong (clean fixture), produced a domain summary, saved via `write_resource`.
  - **Venue Resolution**: read the summary back via `read_resource` (confirming the resource handoff actually works end-to-end), resolved to a real venue (IEEE ICC 2026, verified via live web search), matched it to the `ieee-conference` template via `list_templates`/`get_template_files` (whose metadata already lists ICC as an applicable venue).
  - **Structure/Drafting**: drafted the real paper content into the template, compiled clean with zero warnings on the first attempt, rendered and visually confirmed no structural issues -- no fix iterations needed.
  - **Humanization**: rewrote a paragraph for sentence-structure variety (all claims preserved), recompiled clean.
  - **Final QA**: caught a real issue -- an uncited, topically-irrelevant bibliography entry (a hallucination-adjacent problem) -- removed it rather than forcing an irrelevant `\cite` into the text, recompiled clean, 1 of 3 round-trips used.
  - Final `cleanup_rendered_pages` left a genuine one-page, submission-shaped IEEE conference PDF with no blank space, overlap, or collapse issues.

This is the last task in the plan -- the paper-writing pipeline MCP server is functionally complete.

---

## Execution Notes

- We go file-by-file in the order above. After each task, I stop and tell you it's ready — you review, ask questions, then we move to the next.
- Before writing any file's code, I present the viable approaches for it; you pick or redirect.
- No commits happen unless you explicitly ask, and none will include AI-attribution trailers or comments.
