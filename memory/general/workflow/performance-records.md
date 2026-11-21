# Reading a project's run records for a performance review

What `scripts/session-stats.py` reads and how to read its tables (`--help` lists every argument).

## Records

- **Which issue a command ran:** each typed command line, and each run-record `start` call in the transcript
  (the script reads both). One session often runs several issues, so attribute by segment, never by session.
- **Size of an issue's change:** the merged PR that closes it; titles without `(#n)` are routine. Fetch the
  window's PRs as the JSON the script reads:
  `gh pr list --state all --limit 400 --search "updated:>=<since>" --json number,state,createdAt,mergedAt,additions,deletions,title,closingIssuesReferences > <folder>/prs.json`
- **Run records:** `.audit/issue-<n>/run.json` and `.audit/plan-issue-<n>/plan.json`, event logs written by
  `scripts/run-record.py` (events listed in its header); read section H for them.
  Section F's churn misses rework the orchestrator does itself; count `rework` events.
- **Defects the owner found after a handoff:** section I lists every message the owner typed in the window —
  their bug reports arrive with no issue number, through a planning command, a plain session, or mid-session on
  other work. Weigh each against the project's checks: a spec, the visual pass, the plan review, the issue critic.

## The script's settings

- **Cost weighting** (`--weights`, default `in=1,cw=1.25,cr=0.1,out=5`): billable-equivalent tokens at
  the ratios of input, cache write, cache read and output prices. Change it only if the price ratios
  change, and say so in the review's record, or the numbers stop comparing.
- **Kinds of work** (`--kinds`): a JSON list matched against PR titles in order, first match wins.

## Reading the tables

- The always-on settings that shape every number: the owner's `~/.claude/settings.json` sets the model
  (a `[1m]` model is why a context can reach 900k), its effort, and `autoCompactWindow` (the build ignores
  that key in project settings). Read the file before comparing weeks — `sessions.json`'s `model` field (table A
  has no model column) says what each session actually ran on, and it has changed mid-run.
- Effort is logged on every assistant record (`effort`, `perTurnEffort`), so which effort a run used is read, not guessed. Repo agents run Sonnet at medium whatever the orchestrator's effort; the built-in Explore runs Sonnet because the spawn names `model: "sonnet"` (unnamed, it inherits the orchestrator's model; `CLAUDE_CODE_SUBAGENT_MODEL` does not reach it).
- Every agent definition runs on Sonnet; the orchestrator on the settings model. Meq weights are
  token-class ratios and do not price the model, so a sub-agent Meq is cheaper in money than an
  orchestrator Meq — say "token-weighted" when quoting the sub-agent share.
- A typed `/compact` also writes a `compact_boundary`, so the script's compact column counts it in both
  halves (`1/1`). The record's `trigger` field (`auto`/`manual`) is the arbiter.
- Do not attribute a tools-per-call change to a harness version without listing every elevated session's version; it has moved with a date window before.
- Session hours are spans, and include sessions left open for a day or more; the owner's latency is the
  ask-wait column.
- Sub-agent cost by agent type is not in the tables: sum per-message-max usage per
  `<session>/subagents/agent-*.meta.json` `agentType`.
- In `run.json`, `suite`, `repin` and `gate` events are each a whole-suite pass. A run's wall-clock is its
  record's first-to-last event, not table A's session hours.
- A `Read` of `<session>/tool-results/*.txt`, or of a scratchpad `mem*.txt`, among an implementation run's largest fill items is the run's memory load read back whole, not a test report.
- A `-RepinSeeds` walk also re-records scripted sessions against the live build. An unchanged `seed-pins.txt` does not make it redundant beside the gate, which only replays.
- Both plan-critic events in `run.json` are logged together, so the time between rounds cannot be measured. Round 1's findings are listed at the top of the round-2 brief (`briefs/02-plan-*.md`).
- Reopened issues: a GraphQL issue search with `timelineItems(itemTypes:[REOPENED_EVENT])`, split by created date so each search returns under 100 issues.

## Filing the issue

Its body is `## Requirements` and `## Technical design`, held to `CLAUDE.md`'s "The two rules"; the evidence and
the memory updates go in the technical design. File it with `gh issue create --label documentation --body-file
<that file>`, then run `/plan-issues` on its number; that run reviews it, may split it, and sends it to
`issue-critic`. The owner reviews the issue.
