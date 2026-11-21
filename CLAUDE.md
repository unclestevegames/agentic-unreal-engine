**Project:** what this game is, which repos it spans and where its design and rules live are in memory's always tier, reached from `memory/index.md`.

**Memory:** **Step 1 of every session, before your first action: read `memory/index.md` and cascade.** Unconditional — you cannot know what memory holds until you have read the index. The rules memory is kept to are the "Memory" section below.

**Workflow:** The user defines each scope of work; there is no standing roadmap. Issues are planned from the user's scope first (`/plan-issues`), then implemented **one at a time** with user checkpoints between them. Do not run ahead, propose sequels, or maintain forward plans unprompted.

## The two rules

**This section is the only place either rule is written down.** Nothing else in this repo — no command, no agent definition, no script — states them in its own words. Everywhere else carries a short reminder naming this section, so there is nothing to keep in sync and nothing to drift. A brief generated for an agent is the one exception: an agent reads only its brief, so the rule it must apply is pasted into it verbatim from here.

### Requirements are minimalist

A requirement says **exactly what changes**, in the language of the game. It names the key interactions with what already exists, and stays close to the changed behaviour. It is never an example, and it never assumes today's game is the game forever.

So a requirement:

- **Is in the language of the game, never of the code.** No classes, files, functions, tests, or how the work gets done. Concrete numbers and named values from the game are fine where they are the clearest way to say it ("the camera sits over the centre of the level at Z=890").
- **Is a testable gate** — the user reads it at a glance and says met or not met, and an agent enforces it pass/fail.
- **Says only what changes.** Behaviour that already holds, and would still hold if this issue were never built, is not a requirement. Neither is "nothing else changes" — a blanket non-change is a wish, not a gate.
- **Does not narrate an example.** A worked case, a walk-through, or a sample line of play explains a requirement; it is not one. Examples are welcome below the requirements, marked as examples — one worked case, never an inventory of the places a requirement reaches.
- **Does not explain itself.** The reasoning, the diagnosis and the prior art are technical design.
- **Does not take today's game as permanent.** A requirement resting on how something happens to be presented or sequenced right now will be wrong the first time that moves. Say the behaviour, not the arrangement that currently produces it.
- **Carries no measured figure by value** — no test counts, wall-clocks, line numbers, digests, or counts of files or content. Every one goes stale. Name the thing and point at where the figure lives.

For a **purely architectural** issue, the requirements instead briefly describe — as if to a non-technical person — what kind of change is being made and what it buys us in the long run. Everything above otherwise applies.

**Everything else in the issue is technical design**, under one `## Technical design` heading, and the user generally will not read it. It is brief for the same reason a requirement is: every paragraph is something the implementer would otherwise get wrong, or spend more than a few minutes finding — an owner's ruling and why, a diagnosis that was actually reproduced, a seam that will not compile, a design sentence the requirement rests on, a pin bump and what it drags along. A paragraph that fails that test is deleted. So technical design:

- **Says only what changes**, like a requirement. It never lists what is out of scope, unchanged or not touched — a blanket non-change is unbounded, and every entry in it is a place the reader now has to check.
- **Never inventories the places a "wherever the game shows X" requirement reaches.** The implementer greps the raw field at implementation time, when the list is true; a list in the body is a hand audit that goes stale.
- **Never restates what the code says.** Name the function or file the implementer should read, not what they will find there — and never a line number.
- **Carries no test script, acceptance criteria or per-layer test plan.** The implementation run plans its own checks from the requirements and drafts the hand test into the PR, where it describes what was actually built.

### Behaviour and architecture are simple and general

All aspects of the game should be as simple and homogeneous as possible, **reflecting the feature as closely as possible**. Simple behaviour and simple code are the goal, and **an exception is a red flag** — not a detail to implement. Where a feature seems buildable only by breaking that, the feature is probably being understood wrongly, and it is rethought before it is built; a rethink that would change what the player gets goes to the repo owner.

These are the shapes to watch for:

- **Two things with very close behaviour or purpose, reached by different code paths.** That is an opportunity to make them one thing.
- **An exception to a rule** — a special case, a carve-out, an "except when", a flag whose job is to suppress the general path. Usually a sign the behaviour is wrong, not that the rule needs a patch.
- **Mirrored or duplicated state**, a second mechanism for a concern one mechanism already owns, another entry in an order-sensitive dispatch, another per-exit-path flag to clear.
- **One fact written out by hand in place after place** — a new thing that has to be spelled out again in a widget, a view, a loader and a test before it works. Each edit is small and obviously necessary, which is why nobody notices the cost until several changes are looked at side by side.

Whenever one appears, **the run that found it decides what to do about it, without asking, and tells the repo owner what it decided** — naming the two things, what each does today, what unifying them would cost, and why it chose as it did. The repo owner is not in the codebase and does not choose refactors; the judgment is simple code that fits how the game is used. Only a fix that would change what the player gets goes to them, as the player-facing decision it is. What must not happen is the exception being quietly implemented and the work moving on; the workaround's bill comes due in the next change.

A small, behaviour-preserving cleanup that can be described in one sentence just gets done. **A fix too large for one sentence never goes in the pull request of the work that found it**: the run files it as a separate issue, builds its own work around the problem with a `TODO (issue#N)` at the workaround, and finishes.

**The cost standard.** What a change costs here is not its size, it is how far it has to spread. The measure is **how many separate places one fact about the game's core content has to be written out by hand** across the views that show it. One fact, one place that owns it, and every view derived from that place. Memory names this game's core content, its facts and its views.

### The contract

- Requirements are the acceptance gate. The change is done when every requirement is met, and not before.
- Requirements **supersede the design docs** — they may carry newer decisions from the user. On a conflict, ask the user, then bring the design docs in line with the requirements.
- **Planning may rewrite a requirement to meet the rules above**, and reports every change — the wording replaced beside the wording that replaced it — so the repo owner can reverse any of them.
- **Implementation may never change a requirement.** A requirement that moves while the work is being built is the goalpost moving: the run discovers the work is hard and edits the target to match. A run that finds a requirement wrong, unbuildable or unjudgeable **stops and asks**; it does not rewrite it and carry on.
- **Never** make a game-design or player-facing-behaviour decision unilaterally — ask. That holds at every stage, planning included. A design-doc sentence that leaves the on-screen result open (orientation, placement, size, colour) is an input to the question, not a substitute for asking it.
- Technical design may change freely during implementation, as long as the requirements are still met.

## Memory

Project knowledge lives in `memory/`, versioned with the work. That is the only memory system here;
when the user says "memory", they mean this one. **This section is the only place its rules are written
down** — every command and agent that touches memory points at it and none restates it.

### What belongs where

**Instructions hold process** that applies to any game development situation and is always in force:
this file, `.claude/commands/`, `.claude/agents/`. **Memory holds what is specific to this project**,
and knowledge or tools that change over time or that only some tasks need.

The line that decides a hard case: a **rule** is process and stays in the instructions; a **date, a
measured figure, or an account of what happened on a past issue** goes stale and is needed only by the
task it touches, so it is memory's. Keep the rule where it is and route its evidence to the leaf that
owns that task.

**Knowledge that would hold for any Unreal Engine game made with agents lives in `memory/general/`**, a
part of memory of its own. It has its own `index.md` tree, whose indexes list only its own files.
Nothing in it points outside it — no path, link or name from the rest of memory or from this game.
`memory/index.md` routes to it like any other directory. Everything specific to this game lives in the
rest of memory. `/clean-memory` enforces the split, as it does every rule here.

### Read it by routing, not by reading it all

Every directory has an `index.md` listing its `*.md` files and subdirectories with a "when to use"
column:

```
| Name | When to use |
| :--- | :--- |
| <name> | <when-to-use> |
```

**A routing condition names the kind of work a command or agent actually does**, specifically enough
that nothing is loaded when it is not needed — "when upgrading the engine version", not "sometimes useful".
Read `memory/index.md`, open every file and subdirectory whose condition fits the task plus anything it
plausibly might touch, recurse into each subdirectory's index the same way, and finish every leaf you
open. A file read to its first page is not loaded.

**One topic per file, and no file is a bucket.** "Pitfalls", "lessons", "notes" as a whole-file topic
means everything lands there and nothing is ever routed away from it. Organize by the task; a trap
lives with the task that hits it. Target under **~8 KB** per file and split the moment a file mixes
concerns — a file too big to route is loaded whole for tasks that need a tenth of it.

**The always tier is budgeted at ~10 KB**, measured in bytes (`wc -c`), for every file marked "always"
plus the indexes on the always path. That is the one place the budget is stated. It is bytes and not
lines because a line count is not a budget: one paragraph on one line reads as one line and can be a
hundred kilobytes. The tier holds active constraints and pointers — never state, never history. Over
budget, move detail into a routed file behind a pointer.

### What earns a place

**One entry, one line: the trap and the fix.** Add a why only where the rule reads as wrong without it.
No incident narrative, no issue numbers, no dates, no "two lessons"/"the general form"/"the tell"
scaffolding.

An entry is kept only where it **measurably improves how work is communicated, how long it takes, or
how many tokens it costs to carry**. Name which of the three, or delete it. These never qualify:

- anything the repo, git log, GitHub, or a one-command check already answers. A memory copy of a fact
  the repo owns rots and then misleads, which is worse than absence;
- a trap whose own error message names the fix;
- a one-off environment incident with no rule attached;
- a restatement of something already in a work product or another memory file.

Prefer deleting to compressing. A wrong entry costs more than a missing one.

### Keeping it true

- **Supersede by deletion.** Git is the archive; live memory is working state. Rewrite an entry when its
  fact changes; when work is abandoned, delete the files and record the restore commit hash. Never keep
  "(superseded …)" annotations, changelogs, or stacked session summaries.
- **Update proactively.** Capture corrections and confirmed non-obvious choices as they happen, in one
  line, with the why. At the end of any session with meaningful changes, re-read `memory/index.md` and
  ask what changed that is not captured. A command that edits no tracked file writes it into an issue
  instead ("How commands end").
- **`/clean-memory` is the pass that reorganizes memory**, and the only one. Every other command and agent
  that writes to memory is held to the bar above — concise, and worth its cost — but **none of them is
  responsible for memory being well-organized beyond saying so when it is not.** Noticing that memory
  has drifted is a thing to report, not a thing to fix mid-task.
- **No subagent routes through memory for what it needs to know.** The orchestrating session reads it,
  injects what each agent needs into its brief, and writes results back afterwards. An agent whose
  *subject* is memory reads it the way `code-critic` reads source — that is reviewing it, not
  consulting it.
- **Memory is private.** Do not reference memory files or their structure in work products or in
  conversation unless the user asks about the memory system. These are notes to yourself — write to
  understand, not to explain.
- **Memory lives on `main` only, never on a side branch** — a long-lived branch that issues build on in
  place of `main`, such as a move to a new Unreal Engine version. A run working toward a side branch reads and writes memory
  in a second worktree on its own branch from `origin/main`, and that branch goes to `main` in a pull
  request of its own.

## How commands end

**This section is the only place this rule is written down.** Every command it names carries a short
reminder pointing here, and none restates it.

There are two families:

- **A `plan-…` command and a triage command (one that turns testers' reports into issues) edit no tracked file in this repo — memory included.** A
  `plan-…` command delivers issues, filed or rewritten, and writes a memory update it finds due into the
  technical design of the issue it files or rewrites. A triage command delivers its notes to testers and
  the issues their reports become, and opens an issue of its own for any change it finds due to its
  instructions, its tool or memory. Either way, the run that builds that issue makes the change.
- **`/implement-issue` and every `clean-…` command end with their work on an open pull request against
  `main`, which they never merge.** An issue whose technical design names a side branch on a
  `**Side branch:**` line goes against that branch instead, with its memory in a second pull request
  against `main` ("Memory"). `main` and every side branch are protected alike; the owner's merge is the
  acceptance.

## Comments in the code

**This section is the only place this rule is written down.** A brief generated for an agent pastes it
in verbatim from here, because an agent reads only its brief.

**Brief, one thought per line, tell the story at a glance.** Skip issue numbers, review history, design-doc quotes, scope notes and "mirrors X" cross-references — that rationale lives in memory or the design docs. Two exceptions: code that *looks* wrong gets a short trailing `//` on the same line, and reminders use `TODO (issue#N)...`, the only place an issue number belongs.

The cross-reference ban is about explaining a thing's OWN shape by pointing at a sibling. It does not reach a numbered registry (a header whose entries say "the Nth user, same shape as X") or an ordered per-tick dispatch, where the neighbour IS the fact being stated and breaking the pattern for one new entry states less. Brief this distinction or reviews keep sending the same comments back.

## Communication with the user

**This section is the only place this rule is written down.** Every command carries a short reminder pointing here, and none restates it.

Everything a run tells the owner — a message, a question, a PR, a report — is written for someone who knows the game and how it is built (the engine it runs on, its code's layers, its data, its tests and tools, the rules in this file) but not the code's names. Their yardstick for a run is "which requirements are met." An issue's requirements are held to "The two rules" instead.

- **Name each thing by what it is and where it comes from, in those terms** ("stand-in copies of the save data, built in test code, which the game itself never writes"). Never put a metaphor, a made-up word or a vague noun in place of one of those concepts; when the honest answer is technical, give it in the terms of how the game is built. A class or function name appears only beside that description, never instead of it.
- **Pin a thing down before describing it.** Read the code; a tool's report is a lead, never the description. No reassurance before you understand the thing, and when corrected, recheck the understanding rather than swapping the word. A zero result from a search is a suspect pattern before it is a finding.
- A claim about a harness setting or behaviour is probed in a fresh process before it is made, and what is said is what the probe showed.
- A question about how something works gets a few bullets, one line each: the answer first, no caveats or side notes, at most one closing question. A bullet covering several named things from the game lists each one's name as a name-only sub-bullet.
- Walking the owner through an external system gives one way to do the thing and stops at the next checkpoint: no alternatives, no optional toggles. If you cannot see their screen, say so and look up the real labels.
- A missing prerequisite is work to do: say what has to be built, what it costs and which part is the long pole, never "which you don't have".
- Lead with whatever touches a stated project rule.
- Unless the owner asked about it, leave out the run's internal process — agent names or IDs, task numbers, critic verdicts, gate steps, retry counts, why some internal objection was overruled — and any detail that did not change what the player gets or what the owner must decide. Plans, briefs and issue-thread progress notes keep full technical detail.
- Ask when a requirement is missing, ambiguous, or contradicts the design docs — before implementing around it.
- A question about what a player sees is asked with a named thing from the game and the named place it appears, in the words a player would use — never abstractly.
- `AskUserQuestion` carries all its own context, because the user cannot see the prose around it: the situation, why it is theirs to decide, and the question, all inside the `question` field. Re-read it as someone arriving cold before sending.
- Internal names are yours: renaming a function, class or helper needs no permission, and what the code calls something is never a question for the owner.
- Bugs found along the way are the run's to place, without asking: small and on the topic of the current work → fix it in this work; big, or unrelated to it → file it as a separate issue and leave it out. Either way the run says what it decided when it decides, and the end-of-run summary names it — never silently expand scope. Only a fix that needs a game-design or player-facing decision goes to the owner, as that decision. A shape whose fix leaves the game the same is not one of these bugs: "Behaviour and architecture are simple and general" says what becomes of it.
- End of a run: restate every requirement back with its verification status, and list any issues opened during the run and which requirements they cover, and say what the run decided about every shape it found. This summary should contain no surprises — anything worth surprising the user with should already have been raised as it happened. **No run tells the owner it is finished while any background task it or its agents started is still running.**

## Minimal-.uasset policy (agents author text, not binaries)

1. All logic in C++. No Blueprint graphs.
2. All UI constructed in C++ (programmatic UMG/Slate). No Widget Blueprints.
3. Game data are JSON in git — never UDataAssets.
4. Permitted binary surface: `.umap` levels, materials, imported art (commit PNG sources beside imports), audio. Pair binary commits with a textual dump (the asset-dump script memory names, run via `scripts/run-ue-python.ps1`) where the asset type supports it.
5. Git LFS for binaries. No Perforce.

## Compact instructions

The auto-compact window is the owner's own Claude Code setting (`/autocompact`), so a long run compacts well before the model's limit. When compacting, keep: the issue or report being worked, the branch, the paths of the run's own files (`.audit/issue-<n>/plan.md` and `state.md`, or the folder the running command keeps under `.audit/`, such as `.audit/plan-performance/<date>/`), which task is in progress, what its check is and what review its plan entry demands, that the run logs every check and verdict to its record, every ruling the user gave this session and every question still open, and the last error text verbatim. Drop file contents, tool output and briefs already written to disk — they are re-read from the files, never from the summary.
