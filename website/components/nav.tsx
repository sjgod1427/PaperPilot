import { GITHUB_URL } from "@/lib/constants";

export function Nav() {
  return (
    <nav className="flex items-center justify-between px-6 py-5">
      <div className="flex items-center gap-2.5 font-pp-mono text-sm font-semibold text-pp-ink">
        <span className="relative h-5 w-5 rounded border border-pp-accent">
          <span className="absolute inset-1 rounded-sm bg-pp-accent" />
        </span>
        PaperPilot
      </div>
      <div className="flex gap-7 font-pp-mono text-xs text-pp-muted">
        <a href="#privacy" className="hover:text-pp-ink">Privacy</a>
        <a href="#connect" className="hover:text-pp-ink">Connect</a>
        <a href="/docs/setup" className="hover:text-pp-ink">Docs</a>
        <a href={GITHUB_URL} className="hover:text-pp-ink">GitHub</a>
      </div>
    </nav>
  );
}
