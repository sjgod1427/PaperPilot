import sys
from pathlib import Path

# helper.txt is a growing knowledge base -- stages append new entries to it
# at runtime, so its live copy must live somewhere persistent and writable,
# not inside the installed/bundled package (which is read-only once packaged
# as a frozen .exe, and whose bundled-data extraction folder is torn down
# between runs anyway). ~/.paperpilot/ is the same persistent-user-data
# directory the template library already uses for this reason.
_BUNDLED_SEED_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
_BUNDLED_HELPER_PATH = _BUNDLED_SEED_DIR / "seed_templates" / "helper.txt"
_USER_HELPER_PATH = Path.home() / ".paperpilot" / "helper.txt"


def _resolve_helper_path() -> str:
    if not _USER_HELPER_PATH.exists():
        _USER_HELPER_PATH.parent.mkdir(parents=True, exist_ok=True)
        _USER_HELPER_PATH.write_text(
            _BUNDLED_HELPER_PATH.read_text(encoding="utf-8"), encoding="utf-8"
        )
    return str(_USER_HELPER_PATH)


HELPER_PATH = _resolve_helper_path()

WRITING_STYLE = """MANDATORY WRITING STYLE for every sentence of prose you draft in this
stage (not a stylistic suggestion -- treat a violation the same as a compile
error):
- No em dashes (the character "—", typed as ---, or the LaTeX --- ligature)
  anywhere in the prose. Use a comma, a period, or a colon instead.
- No "not only X but also Y" constructions, or other rhetorical parallelism
  used as a crutch (e.g. "just as X, so too Y", "both a A and a B").
- No analogies or metaphors, unless the research materials themselves use
  one -- explain the actual mechanism directly instead of comparing it to
  something else.
- Write plainly and directly: state the claim, then the evidence, in the
  shortest form that is still precise. No hedging filler, no rhetorical
  flourishes."""

KEY_LESSONS = """Quick reference (see helper.txt at the path above for the full
playbook and worked examples):
- Zero compile warnings does NOT mean the page looks right. Always render and
  actually look at every page image, not just the warnings list.
- Blank space has more than one root cause, and the wrong fix compiles clean
  while still looking broken. In order of what to check:
    1. Column-fill stretching (flushbottom default) -> fix with \\raggedbottom.
       Only the right fix if you see Underfull \\vbox warnings at a column
       break.
    2. A fixed-size placeholder box (e.g. a photo slot) -> adding more text
       will NOT shrink it, no matter how much you add. Fix by giving it real
       content (e.g. an actual placeholder image) instead of leaving it empty.
    3. Automatic last-page column-equalization -> a gap between two blocks
       that each look fine individually. Fix with \\newpage between them.
    4. Genuine content shortfall -> one column (often the one carrying a
       shorter section like Related Work) simply runs out of material before
       its facing column does, even with \\raggedbottom already in place. This
       is not a LaTeX bug and none of the fixes above apply -- the fix is more
       substantive content in the thinner section, which is exactly what the
       page-maximization instruction above is for.
  Diagnose which of the four it is before picking a fix -- don't apply all
  of them at once, or you won't know which one the document actually needed.
- Overfull \\hbox warnings in narrow columns: try \\usepackage{microtype}
  first (free, no wording changes), then \\emergencystretch=2em if that's not
  enough. Only reword text as a last resort.
- Synthetic/example data in figures must stay physically plausible (e.g.
  latency can't go negative) -- sanity-check generated values, not just
  whether the chart renders."""


def structure_drafting_prompt(
    project_dir: str, template_id: str, research_folder: str, max_retries: int = 5
) -> str:
    """Stage 2 instructions: draft the paper, then compile/inspect/fix until clean."""
    venue_md_recovery = ""
    if not (Path(project_dir) / "venue.md").exists():
        venue_md_recovery = f"""
{project_dir}/venue.md does not exist yet, even though Venue Resolution is
supposed to have created it. Before doing anything else, recreate it now:
gather whatever venue guideline content is still available to you (your own
context from this conversation if Venue Resolution ran earlier in it,
otherwise read_resource({project_dir!r}, "venue_resolution") for whatever was
saved there) and call write_project_file({project_dir!r}, "venue.md", ...)
with the venue name, paper type, guideline content, and source URL(s) if you
can still recall them -- say plainly if a URL can no longer be recovered
rather than omitting it silently. Do not proceed to the rest of Step 1 until
this file exists.

"""
    return f"""You are running the Structure/Drafting stage of the paper-writing pipeline.

Project directory (where you will draft and compile): {project_dir}
Template to use: {template_id}
Research materials: {research_folder}
Maximum fix iterations before stopping and asking the user: {max_retries}

{WRITING_STYLE}

Step 1 -- Draft:
{venue_md_recovery}Call read_project_file({project_dir!r}, "venue.md") first to learn the
venue's page limit and formatting constraints. Call get_template_files with
template_id "{template_id}" -- this returns {{filename: content}} for every
file the template needs -- and call write_project_file({project_dir!r},
filename, content) once per entry to write each one into {project_dir}
(binary assets come back base64-encoded; decode before writing, or use
write_file with the raw path if that's easier for binary content).

Read the research materials: call list_directory({research_folder!r}) to see
everything in it, then for each file call read_file(path) for code/data/
notes/config, read_image(path) for plots/figures, or render_pdf_pages(path)
then read_image on the resulting pages for reference paper PDFs (call
cleanup_rendered_pages(path) once you're done with each). Draft the paper's
content and call write_project_file({project_dir!r}, "main.tex", content)
to write it, following the template's existing structure and sections, and
following the mandatory writing style above throughout. Use the best plots
and results from the research materials as figures and tables, placed in
whichever section they actually belong to, not bunched at the end. For every
figure you actually use, call copy_file(source_path, {project_dir!r} + "/" +
filename) to bring it into the project directory and reference it with a
relative path in \\includegraphics -- do not reference a figure at its
original location in {research_folder}, since the project directory needs to
be a self-contained submission package, not dependent on the research folder
still existing at that path later.

Treat the venue's page limit as a target to use, not a ceiling to stay
comfortably under. Draft toward it: give related work, experiments, ablations
and discussion the depth the research materials actually support rather than
the shortest version that technically covers each section. A paper that
compiles clean but sits well under the page limit has left content on the
table -- prefer expanding on real material from {research_folder} (more
baselines, more analysis of existing results, more discussion of
implications) over padding with filler.

Step 2 -- Compile and check:
Call compile_latex({project_dir!r}). If pdf_path is None, read log_text to
find the exact error, fix it (read_project_file({project_dir!r}, "main.tex")
to see the current content, then write_project_file with the corrected
content), and try again. If warnings is non-empty, that's a real signal to
fix (see the lessons below) even though the PDF still compiled.

Step 3 -- Render and visually inspect:
Call render_pdf_pages on the resulting PDF -- this returns a list of PNG page
paths -- and call read_image on every single one to actually look at it, not
just check that the list is non-empty. Look specifically for: blank regions
that shouldn't be there, collapsed or overlapping tables, figures colliding
with text, figures or tables far from the text that references them, and
orphaned headings at the bottom of a column. Also compare the page count
against the page limit in venue.md (read_project_file({project_dir!r},
"venue.md")) -- if the paper sits well under that limit, that counts as an
issue to fix in Step 4 (expand the thinner sections), same as a blank region
or a compile warning.

{KEY_LESSONS}

For anything not covered above, call read_file({HELPER_PATH!r}) for the full
playbook and worked examples before guessing at a fix.

Step 4 -- Fix and repeat:
If Step 2 or Step 3 found anything, fix main.tex (read_project_file, edit the
content, write_project_file) and go back to Step 2. Track how many fix
iterations you've done. If you reach {max_retries} iterations and issues
remain, stop looping -- report to the user exactly what's still wrong and let
them decide how to proceed, rather than looping forever.

Step 5 -- Done:
Once compilation is clean (no warnings) and your visual inspection of every
page found no issues, call cleanup_rendered_pages on the PDF so only the
final compiled PDF remains, not the intermediate page images.

Step 6 -- Extract paragraphs for Humanization:
Call read_project_file({project_dir!r}, "main.tex") to get the finalized
draft and extract every paragraph of body prose, in the order they appear --
the same scope Humanization uses:
skip equations, tables, figures, citations, labels, and code listings,
extracting only the surrounding prose paragraphs. Call
write_project_file({project_dir!r}, "paragraphs.md", ...) with each
paragraph under its own numbered heading (## Paragraph 1, ## Paragraph 2,
and so on) in that same order, so Humanization can map each one back to its
exact position in main.tex.

Step 7 -- Contribute back:
If you had to diagnose and fix a structural problem that isn't already
covered by the lessons above or in {HELPER_PATH} (read_file({HELPER_PATH!r})
if you haven't already this run), call read_file({HELPER_PATH!r}) to get the
current content, then write_file({HELPER_PATH!r}, ...) with that content
plus a new entry appended describing the symptom, the root cause, and the fix
that actually worked -- the same level of detail as the existing entries.
This is how the playbook grows for the next paper that hits the same issue.

If the fix belongs to the template itself -- a class/package setup issue
(wrong/missing required field, a package that needed adding) that would
recur for every paper using template_id "{template_id}", not something
specific to this paper's content -- and this template_id was added to the
user's library via add_template_to_library (by you or an earlier stage this
run), call add_template_to_library again with the same template_id and the
corrected files/metadata, so the fix is permanent for every future paper
targeting this venue instead of only living in {HELPER_PATH} and this one
paper's main.tex. Bundled seed templates cannot be patched this way (the
library never writes into the seed directory, and a same-id entry added to
the user library would be shadowed by the seed one, not override it) -- for
those, the {HELPER_PATH} entry is the correct and only persistence
mechanism.

Step 8 -- Update the approach log:
Call append_project_file({project_dir!r}, "approach.md", ...) with a
"## Stage 2: Structure/Drafting" section containing: how many fix iterations
it took, what each issue was and how you fixed it (structural defects from
Step 3, warnings from Step 2, page count vs. the venue's limit), the final
page count, and how many paragraphs were extracted to paragraphs.md. If you
appended anything to {HELPER_PATH} or patched a template via
add_template_to_library, note that here too so it's easy to find without
re-reading the full helper.txt diff. Do not skip this call."""
