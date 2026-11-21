# Reaching the editor's MCP server

Starting, stopping and connecting to it, and sending calls from a script. The calls themselves are
`mcp-patterns.md`.

## Reaching the editor

- `powershell -File scripts\ue-editor.ps1 status` → "MCP server up" or "NOT reachable" (exit 1 when down — not an error, just the answer).
- Start: `powershell -File scripts\ue-editor.ps1 start -Project '<abs .uproject>'` — `-Project` is REQUIRED (bare `start` throws); launches non-hanging and polls until MCP answers at 127.0.0.1:8000/mcp (~60-90s cold).
- That launch is SlateInspector-blind; MCP-only work (materials, properties, assets) is fine on it, anything needing Slate wants the visible launch in `pie-console.md`.
- A fresh editor opens its STARTUP map — `SceneTools.load_level` first, always.
- Stop: `powershell -File scripts\ue-editor.ps1 stop`. The editor must be stopped before any `Build.bat` run (it holds the DLLs).
- **Single-quote every Windows path argument** — `-Project c:\github\...` unquoted gets its backslashes stripped by the shell layer before PowerShell sees it (`c:github...`).

## Transport

- CLI: `python scripts\ue_mcp.py call <toolset> <tool> --args-file <file>` — args ALWAYS via `--args-file` written with `Set-Content -Encoding ascii` (PowerShell 5.1 mangles inline JSON). `describe <toolset>` dumps that toolset's schemas (~16KB — prefer this file).
- **Redirecting that CLI's stdout in PowerShell writes a UTF-8 BOM**, so reading the file back with a plain `json.loads` dies on `Unexpected UTF-8 BOM`. Read with `encoding="utf-8-sig"`, or skip the round trip and use `McpSession` in-process.
- Many calls in one session: `sys.path.insert(0, r"<repo>\scripts"); from ue_mcp import McpSession, texts_of; s = McpSession("http://127.0.0.1:8000/mcp", 120); s.connect()` then `res = s.tool_call("call_tool", {"toolset_name": t, "tool_name": n, "arguments": a})`; parse `json.loads(texts_of(res))` → payload usually under `"returnValue"`.
- **The session id goes stale unpredictably** — `-32600 Unknown session id` means re-`initialize` (a new `McpSession` + `connect()`) and retry, not a real failure. `ue_mcp.py` does not retry for you.
- **Editor Python that touches Slate must run INSIDE the live editor**, not the headless commandlet — a script that types the console command into the editor's status-bar Cmd box and waits for a line the command itself logs. Needs a VISIBLE editor.
- **A `/Game/...` argument passed through Git Bash arrives as a Windows path** (`C:/Program Files/Game/...`) and the script reports the asset missing. Prefix `MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'`, or call it from PowerShell.
