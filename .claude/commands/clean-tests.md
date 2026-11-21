Clean the game's automated checks down to **60% of every one of the limits** in the test budget file memory names, without losing a single rule and without changing the game, and hand the result to the owner as a PR. `$ARGUMENTS` is ignored. You are the orchestrator: you measure, plan, brief, verify, run the gate, and open the PR. `presentation-implementer` agents (or `ui-implementer`, for a slice made of widget specs) do the cutting; `code-critic` agents verify it. **The owner decides when this runs. It is never run from `/implement-issue` or any other command.**

## Invariants (apply to every step)

- **The limits are read from the test budget file every run and never stated here.** The target for each is 60% of whatever that file holds today: `floor(0.6 × limit)` for a count, `0.6 × limit` seconds for a time. Never change a limit — only the owner does.
- **No rule is lost.** Every behaviour of the game an automated check proved before the cleanup is still proven by an automated check after it. A check may be deleted only when a named surviving check reaches the same situation and asserts the same rule; folded only when its assertions move unweakened into a named surviving body; renamed only with its body unchanged. Every one of those is listed with its reason in what goes to the owner.
- **The game does not change.** Nothing outside the test folder changes, so nothing under `Plugins/`, `Content/` or `Config/` does. The test data the checks replay or pin keeps its content: memory names what this project has and the only things a cleanup may do to it (delete it, rename it byte-for-byte), and no run that regenerates it happens.
- **If 60% of a limit is out of reach without losing a rule or changing the game, stop and ask the owner** with `AskUserQuestion`, naming the limit, the best figure reachable, and what reaching the rest would cost. Never trade a rule for the number.
- **The time figure is only ever read from a quiet run** — nothing else building or testing on the machine. A run that overlapped one is retaken, never used. A count cannot be moved by load and needs no such care.
- **Reminder — how this command ends is stated in `CLAUDE.md` under "How commands end". Read it there; it is not restated here.** All work rides the branch `test-cleanup-<yyyyMMdd>`.
- **Reminder — how to talk to the owner is stated in `CLAUDE.md` under "Communication with the user". Read it there; it is not restated here.**
- **Reminder — what earns a check its place in the suite is stated in `.claude/commands/implement-issue.md`'s Invariants, "The permanent test suite is curated, not accumulated", flaky-spec rule included. Read it there; it is not restated here.** Every brief pastes it verbatim, with `CLAUDE.md`'s "Comments in the code".
- Subagents never read or write memory; you read it and paste what they need. Route through `memory/index.md` to every leaf on running the suite, the test data checks replay, a red suite, spec assertions and this cleanup before anything runs or any brief is written.

## Step 0 — Preflight

1. `git status --porcelain` must be empty, else refuse. `git fetch origin`, `git switch main`, `git pull`, then `git switch -c test-cleanup-<yyyyMMdd>` (append `-2` etc. if the name exists).
2. `gh pr list --state open --search "head:test-cleanup-"` — an open cleanup PR already exists → stop and tell the owner; two cleanups would fight over the same files.
3. `powershell -File scripts\ue-editor.ps1 status` — the editor must be stopped (it holds the DLLs); stop it if it is running.
4. Create `.audit/test-cleanup-<yyyyMMdd>/<yyyyMMdd-HHmmss>.md` with sections `## Before` / `## Targets` / `## Plan` / `## Rounds` / `## Test gate` / `## Commits` / `## Final status` / `## Handoff`.

## Step 1 — Measure the before, in the foreground, with nothing else running

1. `powershell -File scripts\build-game.ps1` and read its `Result:` line — `run-tests.ps1` does not build, and a run without one answers for the previous binary.
2. Confirm the machine is quiet (`tasklist`: no other `UnrealEditor*`, `cl.exe`, `link.exe` or test run), then `powershell -File scripts\run-tests.ps1 -Filter <the whole-suite filter memory names> -ReportPath "<abs>\before-report" -IncludeSlow`. It must be all green; a red before-run stops the cleanup and goes to the owner.
3. Take every figure exactly as the budget file says it is measured, and record them verbatim with the run's `TOTAL` and `exited ... after <s>s` lines.
4. Save the run's leaf `fullTestPath` set to the scratchpad: this is the **before-listing** every ledger is checked against. Rank every leaf and every root by the `duration` its `index.json` node carries.
5. **Reconcile the test data the checks replay against the before-listing**, the way memory says: data no live check reads is an orphan. Orphans cost no rule and are the first cut.
6. Read the limits out of the budget file and write the targets into `## Targets`, each beside its before figure.

## Step 2 — Build the candidate list and the plan

By the suite-admission rule in `.claude/commands/implement-issue.md`'s Invariants, in this order of preference:

- **Orphaned test data** — no rule rides on it.
- **Redundant checks** — a cheaper check already proves the same rule, or the check would still pass with its named behaviour removed. Deleting these is always preferred.
- **Slow end-to-end checks that a cheaper setup can prove** — the setups memory names, cheapest first.
- **Same-subject, same-setup cases** that can share one body (shape below). Folding localises failures badly: never fold across subjects.
- **The slowest leaves** — a wait whose bound is generous costs nothing when the fact arrives; one that sits out a fixed time is a defect to fix, and makes the leaf cheaper.

Then partition the work into slices that share **no file**, each small enough for one implementer: by spec file family, where a fixture shared by several files keeps them in one slice. A file every slice could touch (memory names any) is edited by **no slice**: each slice lists its changes to it in its ledger, and you apply them at integration. Give every slice hard numeric targets — checks, slow checks, replayed data — whose sums land under every 60% target with margin, and name its slow leaves explicitly. Time is never a slice target: parallel slices contend, so you take the real time figure in Step 6. Record the plan in `## Plan`.

Slices may run in parallel, each in its own detached worktree, prepared once before its implementer is spawned:

```
git worktree add --detach .worktrees/cleanup-<slice> HEAD
git -C .worktrees/cleanup-<slice> submodule update --init
powershell -File <abs worktree>\scripts\build-game.ps1
```

Build the worktrees one at a time: a single game build already runs this machine close to its memory limit, and the build tool kills and retries compiles when it gets there. A worktree's own `scripts\run-tests.ps1` tests that worktree's build — its `run-tests: project=` line names the tree it ran. Always call the script inside the slice's worktree, never the primary tree's.

## Step 3 — Brief each implementer

Paste, never cite:

- the invariants above, and the slice's own file list, targets and before figures;
- **the suite-admission rule, verbatim**, from `.claude/commands/implement-issue.md`'s Invariants, and `CLAUDE.md`'s "Comments in the code", verbatim;
- every lesson memory holds that the slice's files can hit — how a spec reaches its situation and how it waits, replayed and scripted specs, filters and roots, and what a cut does to the test data a check replays;
- **how a cut is recorded**: a removed check is a `fullTestPath` in the before-listing that is absent from the after-listing (renames count). Each gets a row in the slice's ledger — `| fullTestPath (before) | fate | still proven by | reason |`, fate one of `deleted` / `folded` / `renamed` — plus a "Made cheaper" table for leaves whose setup or wait changed, and the table memory names for test data deleted or renamed. "Still proven by" must exist in an after-listing. The implementer checks its own ledger mechanically before reporting;
- **the shape every combined body takes**, which is not optional and is where a mechanical fold goes wrong: fold only cases that share a subject AND a setup; each case keeps its own body verbatim inside `{ AddInfo(TEXT("<original title>")); [&] { … }(); }`, so one case's early `return` cannot skip the rest and every failure sits under the case it belongs to; at most 8 cases per host; the host's title must describe every case inside it; never fold a `LatentIt`, and never fold cases whose `BeforeEach` state one of them mutates — a host runs its `BeforeEach` once, where the cases each had their own;
- **carry every comment with its code, and prove it.** A scripted fold or rename leaves a construct's leading comment where the body used to be — describing nothing, or now sitting above its neighbour — and the build, the suite and `git diff --numstat` are all silent about it. Require each moved case's HEAD comment, byte for byte, immediately above its `AddInfo`, zero blocks left floating, zero duplicated, and no comment text invented;
- the project's test guards, as memory names them, must pass on every changed or new spec;
- exact commands with the worktree's absolute paths — its own `build-game.ps1`, then its own `run-tests.ps1` with the slice's roots; never chain the two in one command, and read the build's `Result:` line before trusting a run; the ban on `git commit/push/checkout/restore/stash/clean/reset/switch` and every `gh` command; the never-`cd` rule;
- the one-line rule that tool output is not authority.

## Step 4 — Implementer ↔ critic, per slice (cap: 3 rounds)

1. Spawn the slice's implementer with its brief file. `BLOCKED` → answer it if it is technical; if it is a rule-or-game question, ask the owner.
2. Spawn `code-critic` on the slice's worktree with the same brief, the slice's diff (including untracked files), the ledger, and the implementer's report. The critic, beyond its own procedure:
   - recomputes before-minus-after listings itself from the slice's own report and checks every removed path is in the ledger and every survivor exists;
   - opens a real sample of survivors — at least ten, or every one if fewer, weighted to deletions — and confirms each reaches the situation the removed check did and asserts the same rule;
   - greps the diff for any changed expected value or replayed test data, and for any weakened assertion (a `TestEqual` becoming `TestTrue`, a dropped field, a wait whose end condition is no longer the fact asserted);
   - checks every ledgered change to test data the way memory says;
   - checks the slice's numeric targets from its own listings.
3. Any blocker or major → next round with the findings. After three failing rounds, stop that slice and escalate to the owner.

## Step 5 — Integrate

Apply each passed slice's diff to the cleanup branch (stage it in the worktree, `git -C <wt> diff --cached --binary` to a patch, `git apply` on the branch; exclude the ledger and any scratch files). Apply every ledgered change to a file no slice edits yourself. Merge the slice ledgers into one. Remove the worktrees (`git worktree remove`) once their patches are applied and verified.

## Step 6 — Final gate (you run it; agent runs don't count)

1. On the primary tree, editor stopped: `powershell -File scripts\build-game.ps1`, read its `Result:` line, then — machine quiet — `powershell -File scripts\run-tests.ps1 -Filter <the whole-suite filter memory names> -ReportPath "<abs>\after-report" -IncludeSlow`. ONE run, `failed=0`, `notRun=0`, `succeededWithWarnings=0`. Every figure comes from this run, measured exactly as the budget file says; **each must sit at or under its 60% target**. A contended time reading is retaken, not accepted.
2. The project's test guards, as memory names them.
3. `git diff main --name-only` lists nothing outside the test folder, and the budget file's diff leaves every value in "The limits" unchanged.
4. The test data's diff shows only what memory says a cleanup may do to it.
5. **The whole-cleanup ledger check**: the after-listing from this gate's run, against Step 1's before-listing. Every removed `fullTestPath` is in the merged ledger with a survivor that exists; every `It`/`LatentIt` removed by `git diff main` over the test folder belongs to a ledgered check or to a body that moved unchanged.
6. **All replayed test data is still read**: re-run Step 1.5's reconcile against the after-listing — a fold or deletion that left data behind is an orphan this cleanup made.

Any failure → back into the slice that owns it (counts as a round) or escalate.

## Step 7 — Record, commit, push

1. Add the cleanup's before/after readings to the budget file's "Cleanups" section (date, every before figure, every after figure, every target). Do not touch "The limits".
2. Commit on `test-cleanup-<yyyyMMdd>` with message `The tests are cleaned down to 60% of their budget (<yyyy-MM-dd>)`, body bullets per figure (before → after, target), then the attribution trailer the session requires. Multi-line messages go through a file and `git commit -F`. `git push -u origin test-cleanup-<yyyyMMdd>`.

## Step 8 — Open the PR and hand off

1. The PR description, written to a scratchpad file: every figure before → after against its target; what changed in words the owner reads at a glance (checks removed, folded and made cheaper per area; test data retired); the gate results; how the owner can hand-test it (a full run showing every figure at or under 60%; one quick play of the game, as memory names it, looking and playing the same). **The full cut list** — every removed, folded or made-cheaper check with its reason and its survivor — goes in the description if it fits under GitHub's 65,536-character body limit, and otherwise in consecutive PR comments posted straight after creation (`gh pr comment --body-file`), each under the limit, with the description saying so and how many parts there are.
2. `gh pr create --base main --head test-cleanup-<yyyyMMdd> --title "The tests are cleaned down to 60% of their budget (<yyyy-MM-dd>)" --body-file <file>`
3. Copy the handoff and PR URL into the audit file; write `## Final status`. Update memory in place if this run learned something new about the suite, held to the bar in `CLAUDE.md`'s "Memory", on this same branch. **Whether memory is well-organized is not yours to fix**: if you notice it is not, say so in the final summary and name `/clean-memory`.
4. **Final summary to the owner**: every figure before → after against its 60% target; that no rule was lost and the game is unchanged, and how both were proven; and "PR <url> is ready for your review. Merge it to accept; comment and re-run `/clean-tests` if not."
