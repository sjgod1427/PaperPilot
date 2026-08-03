# PaperPilot

An MCP server that turns a research folder — code, data, figures, notes — into a compiled, submission-ready academic paper. Runs entirely on your machine; nothing is ever uploaded.

**Website:** [sjgod1427.github.io/PaperPilot](https://sjgod1427.github.io/PaperPilot/)
**Download:** [Latest release](https://github.com/sjgod1427/PaperPilot/releases/latest)

## What it does

Point PaperPilot at a research folder and it runs a five-stage pipeline:

1. **Screening** — checks the research for issues that would sink a submission (test-set leakage, statistical-validity problems, illegible figures, cross-file numeric mismatches) before writing a word.
2. **Venue resolution** — figures out the target venue's real formatting rules and page limits, or helps you pick one.
3. **Structure & drafting** — writes the paper into a real LaTeX template, filling every page it's allowed to.
4. **Humanization** — rewrites the draft for plain, direct academic prose.
5. **Final QA** — checks the compiled paper against the source material for hallucinated claims before calling it done.

## Using it

Download `PaperPilot.exe` from the [latest release](https://github.com/sjgod1427/PaperPilot/releases/latest) and run it — see [INSTALL.md](INSTALL.md) for the full setup for Claude Desktop, claude.ai, or Claude Code. The [website](https://sjgod1427.github.io/PaperPilot/) walks through the same steps interactively, including a live connection checker.

## Repository layout

- `src/paper_writing_pipeline/` — the MCP server (Python, `uv`-managed).
- `website/` — the marketing/distribution site (Next.js, static export, deployed to GitHub Pages via `.github/workflows/deploy-website.yml`).
- `tests/` — Python test suite (`uv run pytest`).

## Development

Python side:
```bash
uv sync
uv run pytest -q
```

Website:
```bash
cd website
npm install
npm run dev
```
