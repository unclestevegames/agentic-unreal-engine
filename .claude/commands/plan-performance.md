Review how this repository's development process has performed over the **four weeks ending today**, diagnose where time, tokens and effectiveness went, attack that diagnosis before believing it, and file what survives as an improvement issue. `$ARGUMENTS` may narrow the question ("why did the last three runs cost so much") or move the window ("ending 2026-09-14"); with none, the window is the last four weeks and the question is everything below. **Reminder — what this command may change is stated in `CLAUDE.md`, or in a file it includes. Read it there; it is not restated here.** Every change it wants goes into the one issue it opens.

This command is agnostic to the project. Everything that belongs to one project — where its transcripts and run folders are, how a PR names its issue, what the kinds of work are, what earlier reviews found — lives in memory. **Read `memory/index.md` and every leaf it routes to this command, before the first measurement.** If a fact you need is not there, find it and carry it into the issue as a memory update, so the next run does not have to find it again.

## What a run costs, and how this one stays cheap

Transcripts are megabytes; never read one whole. The measurement script reads them and prints tables; you read the tables. Read a single session closely only through the script's per-session mode, and only the few sessions the tables single out. Keep everything you write in one folder, `.audit/plan-performance/<today>/`, so a compaction loses nothing.

## Step 1 — Measure (the script, not your memory)

Run the measurement script the memory leaf names, with the project's arguments from the same leaf, over the window. Save its full output to the folder. It gives, for every session in the window: cost as billable-equivalent tokens, API calls and tools per call, peak context and whether compaction ever fired, hours and the hours spent waiting on the owner, asks, agents spawned, critic verdicts, the harness version and model. It aggregates per issue (with the size of the merged change), per week, per kind of work, and per planning session; it counts churn from the run folders (rework briefs per implementer brief, critic rounds); and for the largest runs it says what filled the context and how it grew.

**Two measurement traps the script already handles, which you must not undo by hand:** the transcript writes one record per content block with the message's usage repeated, so usage is counted once per message; sub-agent transcripts carry partial usage per block, so the per-message maximum is taken. If you compute anything yourself from a transcript, honour both.

## Step 2 — The angles, every one answered

Answer each with a number from the tables, a quoted line from a session, or "not measurable from what we keep" — never from recollection. A review that answers only the first is the one that gets the cause wrong.

1. **Cost per unit of work, normalised.** Cost per changed line by kind of work and by week. A week of novel work is not a worse process; a rise inside one kind is.
2. **What fills the context, and whether it ever empties.** Peak context per run; the share that is the orchestrator's own retained output (reasoning included), tool results, harness attachments, images; API calls per run and tools per call; whether compaction fired at the configured window or at all, and whether any compaction was the owner's own.
3. **Churn.** Rework briefs per implementer brief; critic fail rate; agents reporting blocked; tasks per plan; issues run twice or followed by an interactive session on the same problem. Where a run kept its record (the script's last section: attempts per task, verdicts, rework causes, findings by the check that should have caught them, asks), read that; inference from brief names is for runs that kept none.
4. **Wall-clock, and whose it is.** Hours per run against agent time; hours spent waiting on the owner's answers, and when in the day the asks landed.
5. **Effectiveness after the handoff.** Read the script's list of every message the owner typed in the window: a report arrives in a planning command's opening, in a plain session, or mid-session on other work. For each one that reports a defect, say which of this project's checks should have caught it — memory names them — or that none could have; one naming an old issue as precedent reports nothing. The list is material to read, never a count of defects. Then issues reopened.
6. **Planning.** Asks and critic rounds per planning session; for the costliest runs, the owner's original issue text against the body the run was briefed from — what was rewritten, demoted or lost, and whether the run later rebuilt to the owner's words.
7. **The harness itself.** Version changes inside the window and what moved with them (tools per call, attachments, compaction); the model and effort settings in force; anything the process could not have caused.
8. **Process and memory gaps.** For the runs with the most rework, read the rework briefs' opening paragraphs and classify each cause: a fact the implementer lacked (is it in a memory leaf the orchestrator would have routed to, and did the brief carry it?), a check the process should have had, a rule misapplied, a genuine defect caught as designed. A cause that recurs across runs without a home in the instructions or memory is the finding.
9. **The premise check.** State what the owner believes went wrong (from `$ARGUMENTS` or the question that prompted the review) and say, with the numbers, whether the evidence supports it — before proposing anything.

## Step 3 — Diagnose, then propose

Write `diagnosis.md` in the folder: the window and the counting rules; a table per angle; the causes, each tied to a run and a quoted line; and the proposals. **Every proposal is costed** against what it adds to the instructions or memory — the owner keeps both lean — and says which of the three it buys: fewer tokens, less clock time, or fewer defects reaching the owner. Levers that are the owner's rather than the process's (model, effort, harness version, a hands-on session with no plan or critic) are listed apart from the proposals, not folded into them. Proposals the evidence does not support are listed as considered and dropped, with the number that dropped them.

## Step 4 — The adversarial pass

Spawn `performance-critic` on a brief file in the folder carrying: the diagnosis verbatim, the path of the script output, the owner's question, and the instruction that it reads nothing but that evidence and the files the diagnosis names. It attacks the measurements (counting, cut dates, weighting, the unit of work), every causal story against its simplest competitor, and every proposal's cost and generality; it names what the diagnosis missed. **Cap: two rounds per version of the diagnosis** — the second re-checks the first's findings only. Fold what survives into `diagnosis.md`, marking each corrected claim; a claim the critic overturned is not softened, it is replaced.

## Step 5 — Report, then file

- **Report to the owner** in the language of the process, not of the files: what they believed and whether it held; what actually moved and why; the proposals with their costs; the levers that are theirs; what stands unreviewed, meaning every change to the diagnosis after the critic's last round, or "nothing". Numbers only where they change what the owner should do. **Reminder — how to talk to the owner is stated in `CLAUDE.md` under "Communication with the user". Read it there; it is not restated here.**
- **File one issue.** Write one instructions-only issue's body to a file with the Write tool, held to `CLAUDE.md`'s rule for requirements, read there. Its requirements are the surviving proposals; the rest of it carries the evidence each rests on, and the memory updates the run found due. That means one dated line per headline number and outlier for the leaf that records earlier reviews, so the next review compares against it, plus any project fact that proved stale or was missing.

  How this project's issue is laid out and labelled, and what follows its filing, is in memory under **Filing the issue**; do it as written there.
