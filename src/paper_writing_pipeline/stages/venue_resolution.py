def venue_resolution_prompt(project_dir: str, domain_summary: str) -> str:
    """Stage 1 instructions: paper type/venue capture and template resolution."""
    return f"""You are running the Venue Resolution stage of the paper-writing pipeline.

Project directory: {project_dir}
Topic/domain summary from Screening: {domain_summary}

Step 1 -- Paper type and venue capture:
Ask the user two things:
1. What type of paper is this: conference, journal, or survey?
2. What is the exact target venue (name or URL)? Make clear they can also
   say "not decided yet" if they haven't picked one.

If the user gives you a specific venue, skip to Step 3.

Step 2 -- Venue recommendation (only if the user has not decided):
Search the web for upcoming venues of the chosen paper type whose
call-for-papers deadline has not passed yet, and that match the topic/domain
summary above. Rank candidates purely on scope/topic fit and having an open
deadline -- do not try to estimate acceptance rate or competitiveness.
Present the top 3 candidates, each with a one-line reason it fits. Let the
user pick one, or give you their own venue instead after seeing the
suggestions.

Step 3 -- Template resolution (once a venue is settled, from either step):
1. Search the web for that venue's actual submission guidelines (formatting
   requirements, page limits, required class/template if they specify one).
   Keep track of the exact page(s)/URL(s) you found this on -- you need them
   for the next step. This applies whether the venue came from the user
   directly or from your Step 2 recommendation.
2. Before doing anything else with these guidelines, call
   write_project_file({project_dir!r}, "venue.md", ...) so the user has a
   durable record of what was found and where it came from. Use
   write_project_file specifically -- not write_resource, which saves hidden
   internal state under .pipeline_state/ instead of a plain file the scholar
   can actually open. Include:
   - The venue name and paper type.
   - The actual guideline content you found: page limit, required
     class/template, formatting rules, citation style, submission deadline if
     relevant -- quote or closely paraphrase what the source actually says,
     don't just state your final decision.
   - The source URL(s) you fetched this from, one per line -- this is a
     required field, not optional detail; if you cannot recall the exact
     URL for something you found, say so explicitly rather than omitting the
     line.
   If you could not confirm any guidelines for this venue (Step 5 fallback
   below), still call write_project_file for venue.md, but say plainly that
   no guidelines could be found and that the generic-article template is
   being used as a fallback. Do not skip this call -- it is a required output
   of this step, not optional bookkeeping.
3. Call list_templates, optionally filtered by the paper type from Step 1.
   Compare each entry's metadata (publisher, format, applicable_to) against
   the venue's actual guidelines you just found. This is a judgment call, not
   an exact string match -- a venue named differently from anything in the
   library can still be the right fit if the format matches (e.g. any
   standard IEEE two-column conference venue fits the ieee-conference entry).
4. If you find a good match, call get_template_files with that template's id
   and use those files as the starting point.
5. If nothing in the library fits, build a new template yourself from the
   guidelines you found -- prefer a standard class (IEEEtran, acmart, llncs,
   article) if the venue's requirements match one, since Tectonic can fetch
   those automatically without needing you to bundle any class file. Then
   call add_template_to_library with a new template_id, proper metadata
   (publisher, paper_type, format, class_name, documentclass_invocation,
   applicable_to, notes), and the files, so the next paper targeting this
   venue does not need to repeat this research.
6. If you cannot find any guidelines for the venue anywhere on the web, fall
   back to the generic-article template, and tell the user clearly that you
   could not confirm the venue's actual formatting requirements.

Step 4 -- Update the approach log:
Call append_project_file({project_dir!r}, "approach.md", ...) with a
"## Stage 1: Venue Resolution" section (created in Stage 0) containing: the
paper type and venue settled on, whether it came directly from the user or
from your Step 2 recommendation (and if recommended, the other candidates
you presented), the template_id you resolved to and whether it was an
existing library match or one you built from scratch, and the page limit
from venue.md. Keep it short -- this is a log entry, not a repeat of
venue.md's full content. Do not skip this call."""
