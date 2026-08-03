export function PrivacySection() {
  const flow = [
    "Claude",
    "private tunnel",
    "PaperPilot (your PC)",
    "your files · Tectonic",
  ];

  return (
    <section id="privacy" className="border-t border-pp-border py-16">
      <div className="mx-auto grid max-w-5xl grid-cols-1 gap-10 px-6 md:grid-cols-[1.1fr_0.9fr]">
        <div>
          <p className="mb-3 font-pp-mono text-xs uppercase tracking-wide text-pp-accent">
            Why it&apos;s built this way
          </p>
          <h2 className="mb-4 font-pp-mono text-2xl font-semibold text-pp-ink">
            Claude doesn&apos;t touch your files. PaperPilot does.
          </h2>
          <p className="mb-4 text-pp-muted">
            Claude Desktop and claude.ai run in the cloud &mdash; they have no way to reach a
            folder on your laptop. So instead of uploading your research anywhere, PaperPilot
            runs locally and opens a private tunnel just so Claude can <em>ask</em> it to do
            things. Every read, every LaTeX compile, every file write happens on your machine,
            under a token only you have.
          </p>
          <p className="text-pp-muted">
            <strong className="text-pp-ink">Claude Code</strong> skips the tunnel entirely
            &mdash; it already runs locally, so it talks to PaperPilot directly, no public URL
            involved at all.
          </p>
        </div>
        <div className="rounded-lg border border-pp-border bg-pp-surface p-6">
          {flow.map((node, i) => (
            <div key={node} className="flex items-center gap-3 py-2 font-pp-mono text-sm">
              {i > 0 && <span className="text-pp-muted-2">&rarr;</span>}
              <span
                className={`rounded-md border px-2.5 py-1 ${
                  i === 0
                    ? "border-pp-accent text-pp-accent"
                    : "border-pp-border bg-pp-surface-2 text-pp-ink"
                }`}
              >
                {node}
              </span>
            </div>
          ))}
          <p className="mt-4 font-pp-mono text-xs leading-relaxed text-pp-muted-2">
            Claude only ever sees what PaperPilot&apos;s tools return to it &mdash; never a
            direct line to your disk.
          </p>
        </div>
      </div>
    </section>
  );
}
