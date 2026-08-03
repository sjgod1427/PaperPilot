from paper_writing_pipeline.stages.structure_drafting import HELPER_PATH


def final_qa_prompt(project_dir: str, venue_name: str, max_roundtrips: int = 3) -> str:
    """Stage 4 instructions: whole-paper consistency/hallucination/venue-fit check."""
    return f"""You are running the Final QA stage of the paper-writing pipeline.

Project directory: {project_dir}
Target venue: {venue_name}
Maximum fix round-trips before stopping and asking the user: {max_roundtrips}

Call read_project_file({project_dir!r}, "main.tex") to get the complete
paper and check three things:

1. Internal consistency: do claims and numbers agree across sections? A
   result quoted in the abstract or conclusion must match what the results
   section and its tables actually show. Flag any contradiction between
   sections (e.g. related work implying a gap the proposed method doesn't
   actually address, or a number in prose that doesn't match its table).
2. Hallucinated claims or citations: is every claim traceable to the actual
   research materials the paper was drafted from -- not invented? Does every
   \\cite reference point to a source that's actually in the bibliography, and
   does that source actually support what it's cited for?

   This check is not just about citations -- it also covers invented
   methodological specifics. Go through the Method/Setup/Experiments
   sections line by line and cross-check every concrete noun, number, or
   technical detail (dataset name, architecture detail like layer type or
   activation function, hardware, batch size, hyperparameter value) against
   what the research materials actually say. A real example this caught: a
   source that only said "12-layer image classifier, evaluated on a
   10,000-image held-out test set" turned into a paper claiming "CIFAR-10,
   32x32 colour images," "3x3 convolutions with batch normalisation and
   ReLU," "measured on a single CPU core," and "batch size 1" -- none of
   which were in the source. Each invented detail was individually
   plausible, which is exactly what made it easy to miss; the paper compiled
   clean and read naturally. If a detail isn't stated in the research
   materials, either describe it generically (e.g. "an image classification
   benchmark" instead of naming a specific dataset) or flag it to the user
   as an assumption that needs confirming -- never fill the gap with a
   plausible-sounding invented specific.
3. Venue fit: does the paper actually comply with {venue_name}'s guidelines
   in venue.md (read_project_file({project_dir!r}, "venue.md")) (page limit,
   required sections, citation style, formatting rules)? Flag any mismatch --
   including sitting well under the
   page limit, which is as much a fit issue as going over it. If the paper is
   under-using the limit, expand the thinner sections (related work, extra
   analysis of existing results, discussion) with real material from the
   research rather than leaving it short.

If you find an issue, fix it directly rather than routing it to a separate
stage as a formal handoff -- but use the same technique that stage would use,
since it's the right tool for that kind of problem:
- Structural/formatting issues: use Stage 2's approach -- fix the LaTeX
  (read_project_file/write_project_file on main.tex), then call compile_latex
  and render_pdf_pages, calling read_image on every returned page to confirm
  the fix actually resolved it visually, not just that it compiles. Call
  read_file({HELPER_PATH!r}) if the cause isn't obvious, and, same as Stage 2,
  call write_file({HELPER_PATH!r}, ...) with a new entry appended if you had
  to work out a fix that isn't already documented in it.
- Awkward phrasing or prose issues: use Stage 3's approach -- rewrite just
  that passage for natural academic style, preserving its technical content
  exactly, then call compile_latex to confirm it still compiles cleanly.
- Consistency or hallucination issues: correct the specific claim, number, or
  citation directly in main.tex (read_project_file, edit, write_project_file)
  so it's accurate and traceable, then call compile_latex to confirm it still
  compiles cleanly.

After fixing anything, re-check all three items again from the top -- a fix
in one place can introduce a new inconsistency elsewhere. Count each full
re-check as one round-trip. If issues still remain after {max_roundtrips}
round-trips, stop, report exactly what's still wrong and where, and let the
user decide how to proceed rather than continuing to loop.

Once all three checks pass cleanly, tell the user the paper is ready as a
submission package for {venue_name}.

Step 3 -- Close out the approach log:
Call append_project_file({project_dir!r}, "approach.md", ...) with a
"## Stage 4: Final QA" section containing: what each of the three checks
found (or "no issues found") and how many round-trips it took to get
everything clean. Do not skip this call.

Then, since this is the last stage, call
read_project_file({project_dir!r}, "approach.md") to get everything every
stage has logged so far, and call write_project_file({project_dir!r},
"approach.md", ...) with that same content but a new "## Summary" section
inserted right after the "# Approach" title, before Stage 0's section. This
summary should condense the full run into a few sentences: venue and
template chosen, how many total fix iterations across all stages, and a
one-line pointer to anything a human reviewing this later should double-check
first (e.g. an assumption that was flagged instead of confirmed, or an issue
that took multiple round-trips to resolve). This summary is what someone
reads first to decide whether they need to read the rest. Do not skip this
either -- both calls are required outputs of this final stage."""
