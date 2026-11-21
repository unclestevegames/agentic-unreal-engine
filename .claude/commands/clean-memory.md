Run a garbage-collection pass over the in-repo memory system (`memory/`). This curates my own notes only — work products (design docs, code, tests) are out of scope and must not be edited by this command.

**Reminder — what belongs in memory, how it must be organized, and what an entry has to be worth to be kept are stated in `CLAUDE.md` under "Memory". Read them there; they are not restated anywhere else, here included.** This command is the pass that enforces them, and **it is not finished while any entry fails either one.**

**Reminder — how this command ends is stated in `CLAUDE.md` under "How commands end". Read it there; it is not restated here.**

**Reminder — how to talk to the owner is stated in `CLAUDE.md` under "Communication with the user". Read it there; it is not restated here.**

## Invariants

- **Nothing is edited until the plan has been attacked.** The pass writes down what it intends to do, an adversary tries to break it, and only then does a file change. A GC pass that edits first and reports afterwards is unreviewable: the owner is shown a diff of notes they have never read, against a state that no longer exists.
- **Every figure in the plan and the report is taken in this run.** No count from recollection, none copied out of a memory file or out of this one. Quote the command that produced each.
- **Deleting is the expected outcome, not the failure case.** A wrong entry costs more than a missing one. The pass is judged on what it removed and on what it made routable, never on having preserved everything.
- **Nothing outside `memory/` is edited** — with one exception the boundary rule creates: an entry that turns out to be process rather than project knowledge is moved into the instructions, because leaving it in memory is the defect. The opposite direction is **reported, never applied**: instruction content that looks like it belongs in memory is a proposal for the owner.

## Preflight

1. `git status --porcelain` must be empty, else refuse. `git fetch origin`, `git switch main`, `git pull`, then `git switch -c clean-memory-<yyyyMMdd>` (append `-2` etc. if the name exists).
2. `gh pr list --state open --search "head:clean-memory-"` — an open memory-cleaning PR already exists → stop and tell the owner; two passes would fight over the same files.

## Inventory

1. Read `memory/index.md` and every directory index beneath it.
2. Check indexes against the filesystem: every `*.md` file listed with a concrete "when to use" condition; nothing listed that is missing; nothing on disk that is unlisted.
3. Measure the always tier against the budget in `CLAUDE.md`'s "Memory" section, **in the unit that section states it in**. Do not restate the figure or the unit here: one number, one place, and this command reads it.
4. Measure every leaf the same way, and note which are over the per-file target.

## Write the plan

Before a single file changes, write `.audit/clean-memory/plan.md`. For every file, one row of what will happen to it and why — **delete / merge into X / split into X+Y / move to the instructions / rewrite / leave** — each with the measurement or the quoted line behind it. Then, the two judgments this pass exists to make, stated per file:

- **Its routing condition, against the standard.** Name the kind of work a command or agent actually does that this file is for. A condition that answers "all of them" is the tell that the file needs splitting, not rewording. A file whose name is a bucket — "pitfalls", "lessons", "notes" — is named for where things land rather than for a task, and everything lands there.
- **Every entry, against the bar.** Which of the three it buys, in one word. An entry that cannot name one is on the delete list, and says so.

Say what the pass will NOT touch and why, so a file that was considered and kept is distinguishable from a file that was never read.

## Attack the plan — before a single file changes

Your own plan is the weakest evidence you will handle: you took the measurements and you already believe them. Spawn `memory-critic` on it, brief as a file like any other agent.

Give it, in the brief file: the whole plan; the commands you ran with their output; **the "Memory" section copied word for word out of `CLAUDE.md`** — an agent reads nothing but its brief, so a pointer would reach it as nothing at all; and the standing git bans and the never-`cd` rule.

- **No file is edited while a `blocker` or `major` finding stands.** Fix the plan and re-run, or drop the item.
- **Cap: two rounds per plan version** (initial, plus one re-check of the fixes). After round two, fix what was found and proceed.
- The critic files nothing, edits nothing, and never talks to the owner.
- It may confirm everything. Say so; a clean pass is a result worth stating.

## Apply, in this order

1. **Delete superseded content.** "(Superseded …)" annotations, stacked session summaries, changelog-style history — rewrite each file to present state only. When deleting substantial work, record the restore commit hash in the surviving entry.
2. **Deduplicate.** Merge entries that say the same thing. A fact that restates a work product becomes a pointer: path plus a one-line hook.
3. **Verify pointers.** Follow every path reference in memory; fix or delete broken ones.
4. **Check staleness.** Spot-check factual claims against the repo; delete or rewrite anything the repo contradicts. Spot-check the always tier hardest — it is loaded unconditionally, so a wrong line there poisons every session.
5. **Reshape.** Split files that mix concerns, merge fragments, rename for clarity, and rewrite every routing condition to match the work it is actually for.
6. **Re-budget.** If the always tier is still over that budget, demote detail into routed files behind pointers until it fits.

## Commit, then open the PR

Commit the result as its own commit so the pruning is a single revertible unit, and push the branch.

The PR description is the report, written to a scratchpad file:

- What was deleted, merged, moved or split — with restore hashes for anything substantial.
- Always-tier size before → after, in the budget's own unit, against the budget. Memory's total size before → after.
- Which files are now routed differently, and what each is for now.
- **Candidates for promotion out of memory into a work product** (design doc, code, ADR), and **instruction content that looks like it belongs in memory**. Propose both; do not apply either without approval.
- Anything ambiguous left untouched, and why.

`gh pr create --base main --head clean-memory-<yyyyMMdd> --title "Memory is cleaned (<yyyy-MM-dd>)" --body-file <file>`

Once the PR is open, send a `PushNotification` (status: proactive) — one line, under 200 characters, e.g. "PR ready: memory cleaned, 4 merged, always tier back inside budget".

**Final summary to the owner**: always-tier size before → after against its budget, what was deleted, merged, moved or split in a line each, the promotion candidates awaiting their word, and "PR <url> is ready for your review. Merge it to accept; comment and re-run `/clean-memory` if not."
