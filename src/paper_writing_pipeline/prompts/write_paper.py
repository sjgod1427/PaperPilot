def write_paper_prompt(research_folder: str, project_dir: str) -> str:
    """Human-invoked entry point: kicks off the full 5-stage pipeline autonomously."""
    return f"""You are starting the paper-writing pipeline.

Research folder (raw materials): {research_folder}
Project directory (where the paper gets drafted and compiled): {project_dir}

Work through all 5 stages yourself, one after another, without waiting for
the user to manually invoke each stage -- the tools below are yours to call
whenever you decide a stage is done and it's time for the next one. Only stop
to ask the user something where a stage's own instructions explicitly tell
you to (for example, paper type and venue in Stage 1) -- otherwise keep going
in one continuous effort.

1. Call the screening_prompt tool with project_dir="{project_dir}" and
   research_folder="{research_folder}", follow its instructions, then save
   the resulting report and domain summary with
   write_resource("{project_dir}", "screening_report", ...). This stage also
   creates {project_dir}/approach.md, which every later stage appends to.
2. Call the venue_resolution_prompt tool with project_dir="{project_dir}" and
   the domain summary you just wrote (read it back with read_resource if you
   need to). Follow its instructions to settle on a paper type, venue, and
   template -- this also writes {project_dir}/venue.md with the guidelines
   found and where they came from.
3. Call the structure_drafting_prompt tool with project_dir="{project_dir}",
   the template id you resolved, and research_folder="{research_folder}".
   Follow its instructions to draft and structurally verify the paper.
4. Call the humanization_prompt tool with project_dir="{project_dir}". Follow
   its instructions to rewrite for natural prose and verify it still compiles.
5. Call the final_qa_prompt tool with project_dir="{project_dir}" and the
   venue name from step 2. Follow its instructions to check consistency,
   hallucinations, and venue fit.

When all 5 stages are done, tell the user where the finished paper is,
confirm it compiled cleanly with no outstanding issues, and point them at
{project_dir}/approach.md for a full record of how the pipeline got there."""
