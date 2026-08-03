"use client";

import { useState } from "react";

type Status = "idle" | "checking" | "connected" | "unreachable";

export function ConnectionChecker() {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState<Status>("idle");

  async function checkConnection() {
    if (!url) return;
    setStatus("checking");
    try {
      const target = url.replace(/\/$/, "") + "/health";
      const response = await fetch(target, { method: "GET" });
      setStatus(response.ok ? "connected" : "unreachable");
    } catch {
      setStatus("unreachable");
    }
  }

  const statusLabel: Record<Status, string> = {
    idle: "Not checked yet",
    checking: "Checking...",
    connected: "Connected",
    unreachable: "Not reachable",
  };

  const statusColor: Record<Status, string> = {
    idle: "bg-pp-muted-2",
    checking: "bg-pp-muted",
    connected: "bg-pp-ok",
    unreachable: "bg-red-500",
  };

  return (
    <div className="flex flex-col gap-3">
      <label htmlFor="tunnel-url" className="text-sm text-pp-muted">
        Paste the URL PaperPilot printed (the part before <code>?token=</code> is fine too)
      </label>
      <div className="flex gap-2">
        <input
          id="tunnel-url"
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://your-tunnel.trycloudflare.com"
          className="flex-1 rounded-md border border-pp-border bg-pp-surface px-3 py-2 text-sm text-pp-ink"
        />
        <button
          onClick={checkConnection}
          disabled={!url || status === "checking"}
          className="rounded-md bg-pp-accent px-4 py-2 text-sm font-semibold text-pp-bg disabled:opacity-50"
        >
          Check connection
        </button>
      </div>
      <div className="flex items-center gap-2 text-sm">
        <span className={`h-2.5 w-2.5 rounded-full ${statusColor[status]}`} aria-hidden="true" />
        <span className="text-pp-muted">{statusLabel[status]}</span>
      </div>
    </div>
  );
}
