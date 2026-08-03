# Running PaperPilot

One download, `PaperPilot.exe`, works with all three ways of using Claude --
pick the one that matches how you use it.

- **Claude Desktop or claude.ai (web)** -- follow Steps 1-3 below. Claude
  runs somewhere that can't see your computer directly, so PaperPilot opens
  a private tunnel and you paste a URL into a connector.
- **Claude Code** -- skip to "Using PaperPilot with Claude Code" near the
  bottom instead. Claude Code already runs on your machine, so it doesn't
  need a tunnel or a URL at all.

## 1. Download and run

Download `PaperPilot.exe` and double-click it. A console window opens and
stays open the whole time you're using PaperPilot -- don't close it.

The first time you run it, it downloads two small helper programs it needs
(this only happens once):
- **cloudflared** -- creates a private tunnel so Claude can reach PaperPilot
- **Tectonic** -- compiles the LaTeX papers PaperPilot writes

This can take a minute depending on your connection. After that, starting
up is instant.

## 2. Copy the URL it shows you

Once it's ready, you'll see something like:

```
======================================================================
PaperPilot is ready.

Paste this URL into Claude's connector settings:
  https://some-random-words.trycloudflare.com/mcp?token=AbCdEf123...

Keep this window open -- closing it stops PaperPilot.
Press Ctrl+C to stop.
======================================================================
```

Copy that whole URL (including the `?token=...` part).

## 3. Connect it to Claude

In Claude Desktop or claude.ai:

1. Go to **Settings → Connectors → Add custom connector**.
2. **Name:** anything you like (e.g. "PaperPilot").
3. **Remote MCP server URL:** paste the URL you copied.
4. Leave the OAuth fields blank -- not needed.
5. Click **Add**.

Then, in a chat, make sure the connector is turned on for that conversation
(there's usually a connectors/tools icon near the message box), and ask
Claude to use it -- for example:

> Use PaperPilot to write a paper from my research folder at
> C:\Users\yourname\Documents\my-research

## Important things to know

- **Your files never leave your computer.** PaperPilot runs entirely on
  your machine; the tunnel just lets Claude reach it. Nothing is uploaded
  anywhere.
- **PaperPilot must stay running** the whole time you're using it from
  Claude. Closing the window disconnects it.
- **The URL changes every time you restart PaperPilot.** If you close and
  reopen it, you'll need to update the connector with the new URL (remove
  the old one, add the new one).
- **Your files are stored on your computer**, in
  `C:\Users\<you>\.paperpilot\`. This is where the auth token, downloaded
  helper programs, and a growing library of paper templates live between
  runs -- safe to leave alone, nothing you need to touch directly.

## Using PaperPilot with Claude Code

Claude Code runs directly on your machine already, so it talks to PaperPilot
straight over a local connection -- no tunnel, no URL, no console window to
babysit. Register it once:

```
claude mcp add -s user paperpilot -- "C:\path\to\PaperPilot.exe" --stdio
```

(Use the actual path to wherever you saved `PaperPilot.exe`.)

Start a **fresh** Claude Code session afterward -- it only checks for MCP
servers when a session starts, so an already-open session won't see it.
Then use it the same way as any Claude Code MCP tool, e.g.:

```
/mcp__paperpilot__write_paper_prompt research_folder="C:\path\to\your\research" project_dir="C:\path\to\output"
```

You do not need Steps 1-3 above for this path -- no tunnel gets created, and
there's no URL to paste anywhere.

## Troubleshooting

**Claude says it can't access your files / asks you to upload them instead.**
The connector's session is probably stale -- remove it from Claude's
connector settings and add it again with the current URL PaperPilot is
showing.

**PaperPilot won't start / closes immediately.**
Try running it from a Command Prompt or PowerShell window instead of
double-clicking, so you can see any error message:
```
.\PaperPilot.exe
```
