"use client";

import { useState } from "react";
import { usePlatform } from "@/lib/use-platform";
import { ConnectionChecker } from "@/components/connection-checker";

type Surface = "desktop-web" | "claude-code";

export function SetupWizard() {
  const platform = usePlatform();
  const [step, setStep] = useState(1);
  const [surface, setSurface] = useState<Surface | null>(null);

  return (
    <div className="rounded-lg border border-pp-border bg-pp-surface p-6">
      <div className="mb-6 flex gap-2 font-pp-mono text-xs text-pp-muted">
        <span className={step === 1 ? "text-pp-accent" : ""}>1. Surface</span>
        <span>&rarr;</span>
        <span className={step === 2 ? "text-pp-accent" : ""}>2. Commands</span>
        <span>&rarr;</span>
        <span className={step === 3 ? "text-pp-accent" : ""}>3. Verify</span>
      </div>

      {step === 1 && (
        <div className="flex flex-col gap-3">
          <p className="text-pp-ink">Which do you use?</p>
          <button
            className="rounded-md border border-pp-border p-3 text-left text-pp-ink hover:border-pp-accent"
            onClick={() => {
              setSurface("desktop-web");
              setStep(2);
            }}
          >
            Claude Desktop or claude.ai (web)
          </button>
          <button
            className="rounded-md border border-pp-border p-3 text-left text-pp-ink hover:border-pp-accent"
            onClick={() => {
              setSurface("claude-code");
              setStep(2);
            }}
          >
            Claude Code
          </button>
        </div>
      )}

      {step === 2 && surface === "desktop-web" && (
        <div className="flex flex-col gap-3 font-pp-mono text-sm">
          <p className="font-sans text-pp-ink">
            {platform === "windows"
              ? "Double-click PaperPilot.exe."
              : "Run PaperPilot for your platform."}{" "}
            It prints a URL. Paste it into Settings &rarr; Connectors &rarr; Add custom connector.
          </p>
          <button
            onClick={() => setStep(3)}
            className="self-start rounded-md bg-pp-accent px-4 py-2 text-pp-bg"
          >
            Next: verify it worked
          </button>
        </div>
      )}

      {step === 2 && surface === "claude-code" && (
        <div className="flex flex-col gap-3">
          <pre className="overflow-x-auto rounded-md bg-pp-surface-2 p-3 font-pp-mono text-xs text-pp-ink">
            claude mcp add -s user paperpilot -- &quot;C:\path\to\PaperPilot.exe&quot; --stdio
          </pre>
          <p className="text-sm text-pp-muted">
            Start a fresh Claude Code session afterward -- it only checks for MCP servers at startup.
          </p>
          <button
            onClick={() => setStep(3)}
            className="self-start rounded-md bg-pp-accent px-4 py-2 text-pp-bg"
          >
            Done
          </button>
        </div>
      )}

      {step === 3 && surface === "desktop-web" && (
        <div className="flex flex-col gap-3">
          <p className="text-pp-ink">Paste the URL PaperPilot printed to confirm it&apos;s reachable:</p>
          <ConnectionChecker />
        </div>
      )}

      {step === 3 && surface === "claude-code" && (
        <p className="text-pp-ink">
          Claude Code connects directly, so there&apos;s no tunnel URL to verify here -- try
          asking Claude to use the <code>paperpilot</code> connector in a fresh session.
        </p>
      )}
    </div>
  );
}
