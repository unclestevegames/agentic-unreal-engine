Run the Unreal MCP audit: empirically verify what UE 5.8's MCP tooling (official plugin + Python fallback, plus third-party servers where useful) can actually do on this machine, record the results, and update the workflow to match reality. This is an audit and process update, not a game feature — but closing gaps with Python IS in scope (see Rules); only genuine engine-side C++ gaps get punted forward. Nothing in the game itself ships from this command. The engine go/no-go decision at the end **belongs to the user**.

## Before anything

**Reminder — what memory holds, how it is organized, and what an entry has to be worth to be kept are stated in `CLAUDE.md` under "Memory". Read them there; they are not restated here.** Everything you write to memory meets that bar. If memory has drifted out of shape, **say so and leave it** — reorganizing it is `/clean-memory`'s job, not yours mid-task.

**Reminder — how to talk to the owner is stated in `CLAUDE.md` under "Communication with the user". Read it there; it is not restated here.**

Read **your role memory**, the audit runbook `memory/index.md` routes this command to — prior audit craft (setup recipes, gotchas, timings, what a re-audit can skip). Apply it; don't re-learn it.

## Prerequisites (check, don't assume)

0. **Engine version check.** Read the installed UE versions from `C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat` and web-search for the latest released Unreal Engine version. If a newer engine version is available than the one installed: **STOP. Do not update anything, do not run the audit.** Report to the user: installed version, newest available version, and (from the release notes) anything MCP-relevant in the newer release. The user decides whether to update first (via the Epic Games Launcher, which is interactive) or audit the installed version as-is.
1. `powershell -File scripts\check-ue.ps1` — the engine the project file names must be installed.
2. A **scratch UE project** to audit against (the real UE project doesn't exist yet): create a minimal C++ project OUTSIDE this repo (e.g. `%TEMP%` or `Documents\UnrealProjects\McpAuditScratch`). A `.uproject` is plain JSON — enable plugins by listing them there (the official MCP plugin and its toolsets/AllToolsets, per the UE 5.8 docs) rather than clicking in the editor. If a step genuinely requires one-time editor UI (e.g. first-launch plugin confirmation), tell the user exactly what to click, once, and record that it was needed.
3. Connect this session's MCP client to the editor's server (default `127.0.0.1:8000/mcp`; the plugin can generate client configs — target ClaudeCode). If connection requires a session restart to pick up MCP config, say so and stop with instructions.

## The checks

Work through these in order, recording evidence (commands, outputs, timings) as you go. For each: try official MCP tools first, then UE editor Python (`UnrealEditor-Cmd <scratch>.uproject -run=pythonscript -script=<abs> -unattended -nosplash -log`), then note if a third-party server (UAIP, StraySpark, chongdashu/unreal-mcp) would fill the gap.

| # | Check | Pass looks like | Blocking? |
| :--- | :--- | :--- | :--- |
| 1 | Inventory: list every available toolset/tool; build a coverage matrix against our needs (levels, actors, materials, textures, UMG, BP, tests, PIE) | Matrix written | — |
| 2 | C++ loop: edit a class on disk → compile (`Build.bat <Project>Editor Win64 Development`) → read errors as text → reload editor | Full loop ≤ ~3–5 min, errors machine-readable | **Yes** |
| 3 | Level authoring: create a level, place ~20 actors with transforms, set properties, **read state back**, save, reload, verify | Round-trip fidelity | **Yes** |
| 4 | Material: create a material instance, set scalar/vector/texture params, assign to a mesh | Works via MCP or Python | No |
| 5 | Asset import: PNG → UTexture2D with explicit settings, referenced from a material | Scriptable (art import pipeline) | No |
| 6 | UMG: create a Widget Blueprint, nontrivial hierarchy, reparent to a C++ base | Either way — UI is C++-built by policy; result decides if WBP shells are ever permitted | No |
| 7 | Blueprint graph: BP subclass of a C++ class with a small event graph | Either way — policy is zero BP logic; calibrates how absolute that stays | No |
| 8 | Automation: trigger `Automation RunTests` and retrieve results (MCP or the CLI runner) | At least one headless path works | **Yes** |
| 9 | PIE: start/stop PIE, capture a screenshot, tail the log | Agent can "see" the running game | **Yes** |
| 10 | Stability: a long working session doing 2–9 repeatedly; count crashes/disconnects | < 1 crash per multi-hour session, recoverable | Tolerable-check |
| 11 | Timings: (a) C++ change→verified, (b) asset change→verified | Recorded as baseline | Tolerable-check |

**Go** = checks 2, 3, 8, 9 pass reliably (MCP *or* scripted fallback) and 10/11 are tolerable. **No-go trigger** = the C++ loop is unusable for agents, or MCP+Python combined can't author the minimal asset surface (levels, material instances, texture import), or instability makes long agent sessions impractical. The fallback is Unity 6 + C# (the pure C++ core ports; only presentation plans change). **Present the evidence and a recommendation; the user makes the call.**

## Approval checkpoint (HARD — after the checks, before any process edits)

Present to the user: the evidence summary per check, the go/no-go recommendation, and the **proposed process changes** — what memory's MCP capability record will say (the coverage matrix), any new/updated files under `scripts/` closing a Python-reachable gap (with a one-line summary of what each does), exactly what will change in each UE-facing agent file, and the memory updates (the engine decision row, the audit runbook, and the call-shape re-verification: which entries changed/were pruned/were added). **Do not edit any agent file, script, or memory until the user approves.** The user may also make the engine go/no-go call here; if they defer it, proceed with the approved process edits and leave the decision open in the report.

## Outputs (after approval)

1. **Memory's MCP capability record** — the living record `/implement-issue` reads to build MCP capability notes: coverage matrix (capability → verified tool → fallback → status), timings, stability notes, third-party-server verdicts, date. Keep it curated (supersede by rewriting), not a log.
1b. **Memory's verified MCP call shapes** — the capability record's companion (`/implement-issue` pastes its entries into agent briefs; division of labor: the capability record says WHAT is possible, the call shapes say EXACTLY HOW to call it). Re-verify every existing entry against the audited engine — run each recorded call shape as written, correct any whose fields/args changed, prune dead ones — and add shapes for every tool this audit exercised that the file lacks. Schemas only change on engine update / plugin-list change / custom toolsets, and this command runs at exactly those moments, so a completed audit leaving stale patterns defeats the file's purpose.
2. **MCP interface code for any Python-closable gap** — new/updated editor-Python scripts (in the folder memory names for them), `scripts/ue_mcp.py`, or `.ps1` wrapper changes, written and verified against the scratch project during this run. This is the default response to a gap surfaced in checks 1-11, not a deferred note — write and verify it before writing the coverage-matrix row that depends on it.
3. **Update the five UE-facing agents** (`.claude/agents/{scene-designer,material-artist,functional-tester,visual-tester,code-critic}.md`): update each agent's **body** — the "Verified toolsets"/tooling-ladder sections — with the verified MCP toolset/tool names, any new shared script from #2, and correct any guidance the audit disproved. NEVER touch the frontmatter `tools:` field: it lists Claude Code tools (Read, PowerShell, …), not MCP tools.
4. **Memory**: the engine decision row (engine decision confirmed or fallback triggered, with the why); the capability record's coverage matrix updated.
5. Delete the scratch project (it's disposable; say where it was).
6. **Update your role memory**, the audit runbook: the procedural lessons of this run — scratch-project recipe, connection sequence, one-time manual steps, per-check timings, stability observations, what a re-audit can skip. Craft only; findings stay in the capability record.
7. Report to the user: verdict recommendation with evidence, what changed in the agent + script files, and what the audit could not determine (to be re-checked once the real UE project exists).

## Rules

- **Notify when you finish or need input**: `PushNotification` (status: proactive) at the Approval checkpoint (waiting on the user before any process edits) and again at the final report (Outputs step 7) — audits run long and the user is often away. One line, under 200 characters, lead with what they'd act on (e.g. "MCP audit done: GO, 3 gaps closed via Python").
- Empirical only: a capability is "verified" if you exercised it here, not because docs/vendors claim it. Anything unexercised is marked `unverified`.
- Never bypass a failure by inventing a manual-editor workflow as the standing process — one-time setup clicks are acceptable and recorded; recurring manual steps are findings.
- This command files no issues and closes no issues against the game's feature backlog — but writing and maintaining the Python interface to MCP (`scripts/ue_mcp.py`, the editor-Python scripts, the `.ps1` wrappers) IS this command's job, not a follow-up for someone else. If a check finds a gap that a UE-editor-Python script can close, write it, verify it against the scratch project, and ship it as part of this run's Outputs — mark the capability `verified (fallback)` in the coverage matrix. Only raise a `/plan-issues` candidate issue when the gap needs real engine-side C++ work (a native `UToolsetDefinition`) that Python has no path to at all.
