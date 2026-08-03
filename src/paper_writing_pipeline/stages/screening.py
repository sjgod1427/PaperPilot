def screening_prompt(project_dir: str, research_folder: str) -> str:
    """Stage 0 instructions: pre-flight screening of a research folder."""
    return f"""You are running the Screening stage of the paper-writing pipeline.

Project directory: {project_dir}
Research folder: {research_folder}

Step 1 -- Discover and read everything in the research folder:
Call list_directory({research_folder!r}) to see every file in it, since you
cannot assume a directory listing tool of your own. For each file found:
- Code, notes, config, data (.py, .md, .csv, .yaml, .txt, .tex, etc.): call
  read_file(path) to read its actual text content.
- Images/plots (.png, .jpg, .jpeg, .gif, .webp): call read_image(path) to
  actually view it -- you need to see the image itself for the clarity check
  below, not just know it exists.
- Reference paper PDFs: call render_pdf_pages(path) to render each page to
  an image, then read_image on the resulting page paths to actually read the
  paper. Call cleanup_rendered_pages(path) afterward to remove the temporary
  page images once you're done reading it.
- Reference links (URLs in notes, not files): note them, but you don't need
  to fetch them at this stage -- venue-agnostic screening only needs to know
  what materials exist, not verify external links.
Paper type and target venue are not decided yet -- do not ask about them,
this stage is venue-agnostic.

Step 2 -- Perform three checks, all static/logical -- do not execute any code:

1. Code logic plausibility: read the code and the claimed results. Does the
   logic plausibly produce those results? Flag anything that looks like it
   couldn't produce the claimed numbers (e.g. a metric computed on the wrong
   split, an obviously mismatched baseline).
2. Image/plot clarity: are the plots and figures clear enough to cite in a
   paper? Flag anything illegible, missing axis labels, or too low-resolution
   to reproduce well in print.
3. Rough completeness: is there roughly enough substance here to write a
   paper at all (code, results, and some explanation of the approach)? This
   is a lightweight sanity check, not the full novelty/publishability
   grading -- that happens in a separate evaluation step outside this
   pipeline.

Step 3 -- Produce a screening report with:
- A short pass/warning verdict for each of the three checks above, with
  specifics (file names, what's missing or questionable).
- A concise topic/domain summary of the work (2-4 sentences): what problem it
  addresses, what approach it takes, and what field/subfield it belongs to.
  This summary is handed to the next stage to help match a target venue.

If any check produced a warning, tell the user plainly that the results may
not be as strong as they could be, and why -- but let them decide whether to
proceed anyway. Never block on a warning; this is a soft gate.

Step 4 -- Start the approach log:
Call write_project_file({project_dir!r}, "approach.md", ...) with a "# Approach"
title followed by a "## Stage 0: Screening" section containing: the
pass/warning verdict for each of the three checks and why, and the topic/
domain summary you produced. Use write_project_file here, not write_resource
-- write_resource saves hidden internal handoff state under .pipeline_state/,
but approach.md is a deliverable the scholar reads directly, so it must be a
plain file at the project root. This is the first stage, so this call
creates the file; every later stage calls append_project_file to add its own
section, building up a running, human-readable record of how the pipeline
reached its final result -- write it so someone with no other context can
follow what happened and why, and use it to spot where something went wrong
if the final paper needs fixing later. Do not skip this step -- it is not
optional bookkeeping, it is one of this stage's required outputs."""
