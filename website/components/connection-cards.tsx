type Card = { title: string; body: string; tag: string };

const CARDS: Card[] = [
  {
    title: "Claude Desktop",
    body: "Double-click PaperPilot.exe. It opens a private tunnel and prints a URL — paste it into Settings → Connectors.",
    tag: "Remote connector",
  },
  {
    title: "claude.ai (web)",
    body: "Identical to Desktop — same exe, same tunnel, same URL. Add it as a custom connector in your browser.",
    tag: "Remote connector",
  },
  {
    title: "Claude Code",
    body: "Runs on your machine already, so no tunnel is created. Register the exe directly with --stdio.",
    tag: "Local, direct",
  },
];

export function ConnectionCards() {
  return (
    <section id="connect" className="border-t border-pp-border py-16">
      <div className="mx-auto max-w-5xl px-6">
        <p className="mb-3 font-pp-mono text-xs uppercase tracking-wide text-pp-accent">
          One download, three ways in
        </p>
        <h2 className="mb-8 font-pp-mono text-2xl font-semibold text-pp-ink">
          Connect it however you already use Claude
        </h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {CARDS.map((card) => (
            <div
              key={card.title}
              className="flex flex-col gap-3 rounded-lg border border-pp-border bg-pp-surface p-6"
            >
              <h3 className="font-pp-mono text-base text-pp-ink">{card.title}</h3>
              <p className="flex-1 text-sm text-pp-muted">{card.body}</p>
              <div className="border-t border-dashed border-pp-border pt-3 font-pp-mono text-xs uppercase tracking-wide text-pp-muted-2">
                {card.tag}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
