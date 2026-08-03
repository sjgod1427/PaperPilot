from paper_writing_pipeline.stages.structure_drafting import HELPER_PATH, WRITING_STYLE

STYLE_GUIDANCE = """You are an experienced professional writer. Write the following
content in a natural, engaging, and authentic style:
- Preserve the original meaning exactly.
- Do not add or remove factual information.
- Vary sentence lengths naturally.
- Use smooth transitions.
- Avoid repetitive sentence openings.
- Avoid unnecessary buzzwords and cliches.
- Use precise vocabulary without sounding overly academic.
- Write with a conversational but professional tone.
- Make the writing flow logically from one idea to the next.
- Read as though written by an experienced human author."""

WORD_COUNT_RULE = """Word count constraint: count the words in the original paragraph and in
the rewrite. They must match exactly. If they don't, adjust the phrasing
(never the technical content) until they do -- do not treat a one- or
two-word difference as close enough."""


def humanization_prompt(project_dir: str, max_retries: int = 3, batch_size: int = 6) -> str:
    """Stage 3 instructions: batched parallel paragraph rewrite + correction pass."""
    return f"""You are running the Humanization stage of the paper-writing pipeline.

Project directory: {project_dir}
Maximum correction retries before stopping and asking the user: {max_retries}
Paragraphs per parallel batch: {batch_size}

Goal: make the prose read naturally, like a person wrote it -- varied
sentence structure, no repetitive LLM-isms, proper academic register. This is
a writing-quality pass, not detector evasion: there is no external
AI-detector API involved anywhere in this stage, and no target score to hit.
Any decision about disclosing AI assistance to a venue is the scholar's own,
as author of record -- not something this stage decides for them.

{STYLE_GUIDANCE}

{WRITING_STYLE}

{WORD_COUNT_RULE}

Step 1 -- Rewrite paragraphs in parallel batches:
Call read_project_file({project_dir!r}, "paragraphs.md") to get the numbered
paragraphs Structure/Drafting extracted. Split them into contiguous batches
of {batch_size} paragraphs each, in their original numbered order (paragraphs
1-{batch_size} in batch 1, the next {batch_size} in batch 2, and so on; the
last batch may be smaller).

Dispatch one subagent per batch using your Agent tool (subagent_type
"general-purpose"), issuing every batch's Agent call together in a single
message so they run in parallel rather than one after another. If you have
no subagent-dispatch tool available in this environment, rewrite each batch
yourself in sequence instead -- slower, but the rewriting rules below apply
identically either way. Give each subagent (or yourself, per batch, if
rewriting sequentially): its batch's paragraph text with paragraph numbers,
the style guidance, the mandatory writing style, and the word count
constraint above, and tell it explicitly to:
- Preserve every technical claim, number, and citation in each paragraph
  exactly -- add nothing that wasn't there, drop nothing that was.
- Return its rewritten paragraphs, numbered the same way, as its response
  text only. It must not write to paragraphs.md or main.tex itself -- only
  you do that, once, after every subagent has returned, so two subagents
  never save to the same file at once.

Once every subagent has returned, combine all the rewritten paragraphs back
into their original numbered order and call
write_project_file({project_dir!r}, "paragraphs.md", ...) yourself with the
complete humanized set, overwriting the extracted originals.

Step 2 -- Substitute humanized paragraphs into main.tex:
Call read_project_file({project_dir!r}, "main.tex") and
read_project_file({project_dir!r}, "paragraphs.md"). For each numbered
paragraph, replace its original text in main.tex's content with the
humanized version from paragraphs.md, matching strictly by paragraph number
and original order of appearance -- not by searching for similar-looking
text, since two paragraphs could otherwise be mismatched. Leave everything
that was excluded from paragraphs.md (equations, tables, figures, citations,
labels, code listings) untouched, then call
write_project_file({project_dir!r}, "main.tex", ...) with the result.

Step 3 -- Verify the rewrite didn't break anything:
Call compile_latex({project_dir!r}). If pdf_path is None, read log_text,
find the specific syntax issue the substitution introduced (a common cause is
an unescaped special character like % or & or _ typed as ordinary prose, or a
\\cite/\\ref/\\label mangled while substituting text next to it), fix just
that issue (read_project_file, edit, write_project_file), and recompile.
Repeat up to {max_retries} times. If warnings is non-empty, check whether the
rewrite introduced a structural regression (call read_file({HELPER_PATH!r})
for diagnosis guidance) and fix it the same way Stage 2 would.

If you reach {max_retries} retries and it still doesn't compile cleanly,
stop, report the specific remaining issue to the user, and let them decide
how to proceed rather than continuing to loop.

Step 4 -- Update the approach log:
Call append_project_file({project_dir!r}, "approach.md", ...) with a
"## Stage 3: Humanization" section containing: how many paragraphs were
rewritten, how many batches/subagents that took, whether the compile check
needed any corrections, and whether any paragraph needed more than one pass
to match its original word count exactly. Do not skip this call."""
