# Agentic Unreal Engine

A starter for making an Unreal Engine game with AI coding agents ([Claude Code](https://claude.com/claude-code)). It is the working method one game's development settled on — the rules every session follows, the slash commands and agents that do the work, the helper scripts they call, and the general know-how gathered along the way — with nothing specific to that game left in it.

Released under CC0: copy it, change it, no attribution needed.

## What is here

| Path | What it is |
| :--- | :--- |
| `CLAUDE.md` | The rules every session works under: how requirements are written, keeping the game's behaviour and code simple, how memory is kept, how a command ends, how to talk to you, and which files agents may author (text, not binary assets). |
| `.claude/commands/` | The slash commands below. |
| `.claude/agents/` | The doers and critics the commands spawn. |
| `scripts/` | Helpers the commands call: the run record, the transcript measurer, the change-footprint measure, and wrappers for the Unreal editor, its engine install, its Python and its MCP server. |
| `memory/` | The agents' notes, in git. `general/` holds know-how for any Unreal game made with agents — the editor and its MCP tooling, importing assets, materials, fonts, capturing the running game, cooking and packaging, UI, tests, and running agents. `project.md` is yours. |

## How to begin

1. Copy `CLAUDE.md`, `.claude/`, `scripts/` and `memory/` into the root of your Unreal project's git repo, beside its `.uproject`. Add `.audit/` to your `.gitignore` — every run keeps its plan and record there — and set `"autoMemoryEnabled": false` in `.claude/settings.json`, so `memory/` is the only memory the agents keep.
2. Fill in `memory/project.md`: what your game is, where its design lives, and its core content. Add your own notes as files beside it and list each in `memory/index.md`.
3. Write the scripts below that your game has to supply.
4. Enable Unreal's Model Context Protocol plugin in your project, so agents can drive the editor, and run `/mcp-audit` once to learn what it can do on your machine.
5. Write an issue, run `/plan-issues` on it, then `/implement-issue`.

## Commands

| Command | What it is for |
| :--- | :--- |
| `/plan-issues <n…>` | Review, and where needed rewrite, GitHub issues so `/implement-issue` can run against them without a further question. Writing the requirements is where a run is won or lost. |
| `/implement-issue <n>` | Implement one issue end to end: a plan of small tasks, one agent per task, each checked and committed, ending on a pull request you merge. |
| `/interactive` | Work alongside you: it writes code, edits the project and builds; you keep the branch, the commits and the hand testing. |
| `/plan-architecture [area]` | Sweep the code for the shapes that make every new piece of core content expensive, and file refactor proposals. It starts no refactor. |
| `/plan-performance` | Review the last four weeks of agent runs — where time, tokens and effectiveness went — and file what survives critique as an improvement issue. |
| `/clean-memory` | Garbage-collect `memory/` against the rules in `CLAUDE.md`, ending on a pull request. |
| `/clean-tests` | Cut the automated test suite to 60% of every limit in your test budget file, without losing a rule or changing the game, as a pull request. |
| `/mcp-audit` | Find out what Unreal's MCP tooling can actually do on your machine, close the gaps with editor Python, and record the results in memory. |

## Scripts you write

The commands call two scripts this starter cannot carry, because they depend on your game's targets and tests:

- **`scripts/build-game.ps1`** — builds your game's editor target with Unreal Build Tool and fails loudly unless UBT reports `Result: Succeeded`.
- **`scripts/run-tests.ps1 -Filter <filter> -ReportPath <folder> [-IncludeSlow]`** — runs your automation tests headless, writes the report to the folder, and prints one summary line carrying `TOTAL=` and `failed=`.

Optional: **`scripts/change-footprint.layers.json`**, an ordered list of `{"name", "prefixes"}` naming your repo's layers. Without it, `change-footprint.ps1` takes each path's first folder as its layer.

Two more that the general notes mention, worth writing when you first need them: an **asset-dump script** (`dump_asset.py`, run through `run-ue-python.ps1`) that writes a text dump beside each binary asset you commit, as `CLAUDE.md`'s asset policy asks; and **`drive-game.ps1`**, which launches the game outside the editor (`-game`) so an agent can drive and watch it.

Anything else a command needs from your game — the filter that runs the whole suite, your test guards, the test budget file — it finds through memory, so name each one in a note.

## Lessons learned

What made the biggest difference, in the order to adopt it.

### 1. Give the agent a memory system

Do this first; nothing else comes close. Without it every session starts from zero, re-derives the same facts and re-makes mistakes you already corrected, and you pay for that in tokens and in your own attention every time.

Any memory beats none. What matters is that it lives **in the repo** — in git, reviewed like code — and that the agent is **told to read it and to update it**, not merely allowed to. The one here is small markdown files, one topic each, each folder with an `index.md` whose "when to use" column lets the agent route to what a task needs instead of loading everything. A small always tier is read every session, held to a budget in bytes (a line count is no budget — one line can be a page), and carries active constraints and pointers only. Notes are organised by the task that needs them, so an agent doing one job doesn't wade through another's.

Two rules matter more than the layout:

- **One source of truth.** A fact that belongs in code, a test or a design doc goes there; memory holds a pointer at most. Memory is for what the repo can't tell you — rationale, your preferences, the traps.
- **Supersede by deletion.** When a fact changes, rewrite it in place; git is the archive. Memory that piles up "(superseded …)" notes and session summaries stops being read.

Two additions worth making early:

- **A decisions file.** Each settled choice with its why, in one line. Without it agents relitigate settled questions or quietly reverse them, because the reasoning was nowhere they would look. When a decision changes, rewrite the line — it is a list of what holds, not a log.
- **A garbage-collection pass.** Memory rots: entries go stale, duplicates pile up, the always tier creeps over budget. Make cleaning it a command you run (`/clean-memory`), not something you hope happens.

### 2. Pair every doer with a critic

One agent does the work; a **separate** agent, in its own context, adversarially checks it against the plan. An agent that has just written something reads it charitably and wants to report success; a fresh one holding only the requirements and the diff does neither. It catches the check that proves internal consistency instead of the actual claim, the "matches the existing layout" nobody measured, the work that drifted past what was asked.

- **Critique the plan, not only the code.** A bad plan produces work that passes review and still isn't what you wanted, and a plan is far cheaper to fix than a branch.
- **Cap the loop.** Two rounds per plan version — the first earns its cost, later ones tend to return one marginal item at a full round's price — then fix what was found and go on, letting the final gate catch the rest.
- **A doer's "tests pass" is a claim, not evidence.** The orchestrating session runs the check itself; the critic verifies by reading, building only when the change needs proof that it compiles, and running a check only on a concrete suspicion.
- **Every brief is a file**, not a chat message. Transcripts expire; files don't, so every instruction to every agent stays reviewable and replayable.
- **The orchestrator reads memory and the design docs; the agents don't.** It puts exactly what each agent needs into its brief, so no agent pays to rediscover the same context.

### 3. Separate requirements from technical design

Every issue opens with **requirements**, in the language of the game, saying exactly what changes — something you can read at a glance and call met or not, and an agent can enforce pass/fail. For a purely architectural change they say instead, as if to a non-technical friend, what kind of change it is and what it buys in the long run. Everything else — diagnoses, file maps, plans of attack — goes under one technical-design heading, which you generally won't read.

- **It gives you one thing to review.** Without it, approving an issue means digging the few lines that matter out of pages of engineering, which is tiring enough that you stop reading carefully — and that is how work you didn't want gets approved.
- **It gives the agent a real definition of done.** "Implement the plan" can't be checked; "the camera returns to the player's hand when combat ends" can.
- **It frees the technical design to change.** Agents find better routes mid-task, and that's good; the requirements stay put.

The rules that hold it together:

- **Requirements supersede the design docs** — they may carry newer decisions. On a conflict the agent asks you, then brings the docs in line.
- **Planning may rewrite a requirement to meet the rules, and reports every change** beside the wording it replaced, so you can reverse it. **Implementation never changes one**: an agent that finds a requirement wrong or unbuildable stops and asks.
- **No game-design or player-facing decision is the agent's to make.** It asks.
- **Bugs found along the way are the run's to place, without asking:** small and on the topic of the work, it fixes them there; big or unrelated, it files them as their own issue. Either way it tells you what it decided. Only a fix that needs a game-design decision comes to you — as that decision.

#### The communication half

The same principle governs what the agent tells you: the game, not the machinery. A line to stamp out:

> "The T10 critic's objection was ignored because…"

You don't know what T10 is, you don't watch the log, and you don't care why an internal objection was overruled. Working out whether it concerns you is pure cost. A detail that didn't change what the player gets or what you have to decide shouldn't reach you.

Every run ends with the requirements read back, each marked verified, plus the issues it opened along the way. Done right, that summary holds **no news** — everything in it was agreed with you when it happened. A surprise in the final summary means something was decided without you.
