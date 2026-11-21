# Running the MCP audit

Setup recipes and gotchas for the run itself. Findings (what the tooling can do) go to
`mcp-audit.md`, never here; the verified call shapes go to `mcp-patterns.md`.

## Scratch project recipe

The scratch project lives outside the repo and is left in place for re-audits — delete it freely if
space is needed and rebuild it this way:

1. A bare C++ project: `.uproject` (FileVersion 3, one Runtime module) + `Source/<Name>/<Name>.Build.cs/.h/.cpp` + `Source/<Name>.Target.cs` + `Source/<Name>Editor.Target.cs`. No template content needed.
2. **`DefaultBuildSettings = BuildSettingsVersion.V7` is REQUIRED in both Target.cs files** — V5 fails against the installed engine with "modifies the values of properties... not allowed".
3. Enable plugins by listing them in the `.uproject` `Plugins` array (no editor UI click): `ModelContextProtocol`, `ToolsetRegistry`, `EngineAssetDefinitions`, `AllToolsets`.
4. Auto-start the MCP server via `Config/DefaultEditorPerProjectUserSettings.ini` — the block is in `mcp-audit.md`.
5. Build once before first launch: `Build.bat <Name>Editor Win64 Development -Project="<abs>.uproject" -WaitMutex`.
6. Launch: `UnrealEditor-Cmd.exe "<abs>.uproject" -stdout -FullStdOutLogOutput -unattended > <logfile> 2>&1`, backgrounded via the harness, not a shell `&`. **`-log=<path>` alone (no `-unattended`, no real redirection) hangs indefinitely at near-zero CPU and never creates a log file** — root cause never found; the `-stdout -FullStdOutLogOutput -unattended` combo worked every time.
7. Poll readiness by curling the MCP port (`curl -s -o /dev/null -m 2 http://127.0.0.1:8000/mcp`) in an `until` loop, not by grepping the log for a magic string.

The step-0 engine-version check reads the installed-engine manifest at
`C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat` (JSON; `AppName` entries like `UE_5.8`).

## Talking to the server directly

Daily use is `python scripts/ue_mcp.py` — it encodes the whole handshake plus two transport gotchas
found after the first audit: the server only streams SSE bodies on **keep-alive** connections
(per-request `Connection: close` clients like urllib get empty bodies), and SSE responses have no
length delimiter (read line-by-line and stop at your response event; read-to-EOF blocks ~15s). The raw
sequence, if the script ever needs repairing: `initialize` (capture the `Mcp-Session-Id` header) →
`notifications/initialized` → `tools/call` with `name:"call_tool"`, session header on every request.

## Two script-level traps

- UE's pythonscript commandlet **escape-processes backslashes** in the `-script` value (`\u`, `\n` in paths get eaten) — always pass forward-slash paths (`run-ue-python.ps1` does this).
- `UnrealEditor-Cmd` exit codes are unreliable for pythonscript success (unrelated log errors pollute them) — judge by a log success pattern (`run-ue-python.ps1 -SuccessPattern`).

## What a re-audit can skip

- The MSVC toolchain check and the scratch-project plugin/config setup, if this machine and project are unchanged — go straight to relaunching and probing.
- Re-discovering toolset names; only re-verify on a UE version change.
