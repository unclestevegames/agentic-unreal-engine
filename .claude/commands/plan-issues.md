Review, and where necessary rewrite, one or more GitHub issues in this repo. `$ARGUMENTS` = the issue numbers. **Reminder — how this command ends is stated in `CLAUDE.md` under "How commands end". Read it there; it is not restated here.** The deliverable is issue bodies that `/implement-issue` can be run against without a single further question — and no longer than that takes.

This command exists because **writing the requirements is where a run is won or lost.** An implementer builds exactly what the Requirements block says, a critic checks exactly that, and both will reason impeccably from a requirement that is wrong. Every expensive failure this project has had started here, not in the code.

## Invariants

- **You are planning, so you MAY rewrite a requirement — and you report every rewrite.** **Reminder — the rules a requirement must meet, and the licence planning has to rewrite one, are stated in `CLAUDE.md` under "The two rules". Read them there; they are not restated anywhere in this file.** The wording you replaced goes beside the wording that replaced it in your report, so the owner can reverse any of them.
- **A game-rules or player-facing decision is still never yours.** Printed wording, timing, what a thing in the game does, who may see what, what is legal when, what is on screen and where. Those go to the owner with `AskUserQuestion`, and their answer is written into the issue body before the issue is called ready. Rewriting *how a requirement is worded* is yours; changing *what the game does* is not, and the line between them is worth a question whenever it is not obvious.
- **Everything else in the body is technical design, and it is yours** — under its own standard in `CLAUDE.md`, beside the two rules: every paragraph is something the implementer would get wrong, or spend more than a few minutes finding, without it. Write it freely, correct it freely, and expect the owner not to read it.
- **A diagnosis is not a requirement.** "The defect is in X" is a hypothesis written before anyone looked, and it has been wrong. Read the code path a requirement names before you write down where the fault lives, and reproduce where you can.
- Ask the owner only what they can see the consequence of in the game. **Reminder — how to talk to the owner is stated in `CLAUDE.md` under "Communication with the user". Read it there; it is not restated here.**
- Repo boundaries: work owned by another repo this game depends on belongs there, and design changes to the design docs (memory names both). An issue filed here that only that repo can deliver is a blocker to file there, not a scope to widen.

## The planning record

Every planning run keeps `.audit/plan-issue-<n>/plan.json` through `python scripts/run-record.py <that file> <event> key=value...` (events in the script's header): `start` when you begin, `ask`/`answer` around every question to the owner, `rewrite` for every requirement you reword, `critic` for every issue-critic verdict, `shape` for every shape the design chooses or the run decides about, `ready` at the verdict. Briefs for the critic live in the same folder under `briefs/`. The review command reads this record; a planning run without one is invisible to it.

## Read before you write

Route through `memory/index.md`. At minimum:

- how the owner wants a scope broken down, split, written and filed;
- where each mechanic is specified in the design docs, and where those docs drift;
- the standing architecture rulings the technical design must not ask anyone to break;
- the failure modes a badly-written issue produces two steps later.

## The checks an issue must survive before anyone is briefed on it

Run these here, not at implementation time. Every one of them has cost a run.

1. **The body is two sections and nothing else**: a leading `## Requirements`, then `## Technical design`, each held to its own rule in `CLAUDE.md`. Labels `feature` plus one `agent:*`. **An instructions-only issue** — one that moves nothing the game is built from, nothing under `Source/`, `Content/`, `Config/` or `Plugins/` — carries `documentation` instead of an `agent:*`, because no agent owns it; `/implement-issue`'s preflight recognises that shape.
2. **Every paragraph of technical design earns its place.** Read each one and ask what the implementer would get wrong, or spend more than a few minutes finding, without it; no answer → delete it. The shapes that keep creeping back are the ones the standard names: a list of what is out of scope or unchanged, an inventory of the places a "wherever" requirement reaches, a restatement of what the code says, a line number, a test script, acceptance criteria, a per-layer test plan. The implementation run plans its own checks from the requirements and drafts the hand test into the PR; nothing you write in those shapes survives to be used.
3. **Every blocker is real and delivered.** `gh issue view <n> --json blockedBy`, then for each blocker read the PR that closed it — its requirement read-back against its own diffstat — not merely its CLOSED state. An issue is closed by a human action, not by a check, so CLOSED says nothing about completeness. Same for every "as issue #N already does" claim in the body: verify it against the file, in one `cat`.
4. **Every "this is the first X in the game" and every "nothing in the game's data does X" claim is checked**, by a script over the game's authoritative data (memory names where it lives) dumping whichever property the claim keys off — never by recollection. Half of them have been wrong, and a false one steers an implementer toward inventing machinery the game already has. **Re-take the survey after any change to that data the issue carries**: one taken before it is a survey of the data the change replaced.
5. **Every design reference resolves**, and says what the issue claims it says — one line per reference: the file, and the sentence the requirement rests on where it is short. Where the issue exists *because* a design sentence is ambiguous, "the doc already says the right thing" is the answer to distrust.
6. **Any layer or diagnosis the technical design names was checked by reading the code path**, not inferred from the symptom. Memory names the layers this repo has.
7. **A change that drags other committed files with it says so in one line** of the technical design — a dependency's pin moving, say, and whatever memory names as rewritten with it.
8. **The issue is one unit of delivered work.** If it is not, say so and propose the split — merging and splitting are the owner's call, and a ruling that reaches into a later issue is a scope question for them, never something to quietly narrow or widen.
9. **Footprint — how far this work will spread, stated before it starts.** List the layers and files the work will touch. Then read what the most recent merged issues **of the same kind** actually cost — `gh pr list --state merged`, `gh pr view <n> --json files`, and `powershell -File scripts\change-footprint.ps1 -Base <baseRefOid> -Head <headRefOid>` for each — and name two things: any **construct these issues had to write out by hand in several places**, and any **file every one of them edited**. Take every count in this pass; never quote one from a file or from memory. **The footprint belongs to your report and the critic's brief, not to the body** — the body carries only what check 10 decided, and only where that changed the issue.
10. **Decision — where the footprint repeats a pattern recent issues already paid for.** Where check 9 finds one, decide by your own judgment whether it gets a refactor issue and, if it does, whether that issue comes first, and file it without asking the owner: a purely architectural body held to these same checks and the adversarial pass below, and where it comes first, this issue marked blocked by it. **Reminder — whose call this is, and the judgment it is made by, are stated in `CLAUDE.md` under "Behaviour and architecture are simple and general". Read it there; it is not restated here.** Do not start it. Report what you decided and why. `/plan-architecture` sweeps the code itself for these patterns and is the owner's to run; naming it to them is telling them it exists, never running it yourself. Finding nothing is a perfectly good result — say so and move on.

## The adversarial pass — run it before the verdict, every issue, every time

You checked your own work above, which is the weakest kind of checking there is. Once a body is drafted and every question the owner needed to answer has been answered, **spawn `issue-critic` on it** and let it attack.

Give it, in the brief file: the drafted body verbatim; the owner's rulings from this session verbatim (those are requirements and are not its to question); every decision you took on a shape, with the issue it filed, if any; **both rules and the technical-design standard copied out of `CLAUDE.md`'s "The two rules" word for word** — an agent reads nothing but its brief, so a pointer would reach it as nothing at all; the design-doc excerpts you relied on; the footprint you took in check 9; and the blockers and "as issue #N already does" claims you are asserting. Give it the standing git bans and the never-`cd` rule, as every brief here does.

- **An issue is not ready to brief while a `blocker` or `major` finding stands.** Fix the body and re-run it, or — where the finding is that a *requirement* is wrong, unbuildable or unjudgeable in a way only the owner can settle — take it to the owner with `AskUserQuestion` and write their answer into the body. A finding on shape is yours to decide, and a decision you logged settles it.
- **The critic never talks to the owner and never edits the body.** Both are yours. Do not pass its findings through to them raw; a finding is an input to your question, not the question.
- Minor findings may be accepted; say in the report which you accepted and why.
- **Cap: two rounds per body version** (initial + one re-check of the fixes) — the plan-critic's cap in `/implement-issue`, for the same reason: the first round earns its cost, later rounds tend to return one marginal item at a full round's price. The second round re-checks the first's findings; anything new it finds is fixed without a third round. The one exception that still blocks: a requirement that cannot be built or judged, which goes to the owner.
- It may find nothing. Say so — a clean pass is a result, and it is not the same as not having run one.

## Output

Report per issue:

- **Requirements: minimalist, or not** — say it plainly either way, so a clean answer is visibly an answer rather than a silence. Where they were not, list every rewrite: **the wording you replaced beside the wording that replaced it.**
- **Architecture: simple and general, or not** — the same, for what the body below the requirements takes for granted. Where it rests on something that is neither, say what you decided about it and why.
- **A Footprint line**: the layers and files the work will touch, plus any repeated pattern check 9 found, what you decided about it and why, and any issue you filed for it — or "no repeated pattern found".
- **A Shapes line**: every shape the technical design chooses — a new mechanism, a new data format, or a second path beside one that already exists — named in one line each, so the owner sees what the design commits the game to; or "no new shape". The critic's evidence lists them; you carry the list.
- **What stands unreviewed**: every edit made after the critic's last round, or "nothing".
- Every question you put to the owner and what they ruled; anything you could not resolve; and a plain verdict — **ready to brief**, or **not ready, and what is missing**.

Edit the body with `gh issue edit --body-file`, writing the file with the Write tool or Python rather than a heredoc, then re-fetch the issue and grep for the new wording to prove the edit landed.
