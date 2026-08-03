import { GITHUB_URL } from "@/lib/constants";

export function Footer() {
  return (
    <footer className="flex flex-wrap items-center justify-between gap-3 px-6 py-10 font-pp-mono text-xs text-pp-muted-2">
      <span>PaperPilot &middot; runs locally &middot; MIT licensed</span>
      <a href={GITHUB_URL} className="text-pp-muted hover:text-pp-ink">
        Source on GitHub
      </a>
    </footer>
  );
}
