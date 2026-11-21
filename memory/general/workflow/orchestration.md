# Running the issue (orchestrator)

## Technical choices

- When the TECHNICAL design admits two acceptable answers and neither is blocked, choose the smaller reversible one, file the deferred half, and report the choice. Handing over a technical decision you are equipped to make is a stall; a player-facing one is never yours.

## Reading requirements

- When a requirement's literal wording would DELETE shipped, deliberately-built work, or would force the design to lie, you are reading it wrong. `git log` what you are about to remove, ask, then write the clarification back into the issue body.
- **A requirement that deletes something RENDERED: grep the design docs for that thing's own paragraph before planning.** The doc usually states what the thing was FOR, and the question worth the owner's round is whether that information is lost or has already moved elsewhere — answer it yourself from the code first, so the ask is one line and not a design debate.
- A requirement with both a stated principle and an enumerated list is TWO requirements — name which one is the gate, in the issue body, before any task plans against it.
- **Check every "all the X in this feature do Y" requirement against the members that PREDATE the feature.** A borrowed component, a reused widget, a shared asset already does something else, and it is keyed by name with no per-feature axis — so the requirement cannot hold without breaking the older caller. The owner may withdraw the requirement rather than clarify it; offer that reading.
- **A technical design that folds several members' rules into one generic test can silently drop one member's guard** - diff each member's current rule against the folded wording before planning, and carry the old rule as that member's row data rather than adopting the paraphrase (saves a plan-review round).
- **Set aside a grep census's false hits by reading each one, never with a `grep -v` on a word** - an excluded word also excludes the production file whose name contains it.

## The task loop

- **Never split a layout's positions from its type sizes across two tasks** — a body box that grew stops overflowing at the old font size, and the intermediate task leaves the suite red through no fault of its own. Sizes are part of the same measured layout.
- **Never do your own task while an agent's task is running.** One binary, one `Intermediate/`, one `Saved/` — a second build compiles the agent's half-written file into the DLL it is about to test, and the tell is a `Tee-Object` "file in use" on the build log, which reads like a machine fault. Park your edit (whole file plus patch, hash before and after) and wait.
- **When a review says "nothing covers X", grep for the BEHAVIOUR before believing it** — specs press buttons and assert submitted JSON, they do not call the widget's internals, so a search for production method names finds nothing and reads as a coverage hole.
- Keep the run's own pre-task baseline and diff LEAF NAMES against it. Never accept an agent's account of what was already broken: a stash cannot remove a regression you committed in an earlier task.
- **An implementer's edit can add OR strip a UTF-8 BOM** - the diff shows line 1 changed with nothing visible. Check `head -c3` of each touched file against `git show HEAD:<f>` and put it back the way HEAD had it (strip: `sed -i '1s/^ï»¿//'`; restore: prepend `﻿`) before the commit.
- `git status --porcelain` before EVERY commit, not just at preflight. A hunk from another workstream is preserved (patch + copy into `.audit/issue-<n>/`), reverted, and surfaced — never committed and never deleted.
- When an agent reports "the file the brief named does not exist", believe it and check the brief. If a brief forbids spec edits but changes a function's input shape, name which specs are authorised.

## Briefs

- Audit a diff against the house comment standard in one command: `git diff HEAD | Select-String '^\+.*(requirement [0-9]|issue ?#|[a-z-]+\.md)'`, then again with newlines stripped and case-insensitively, because a wrapped comment hides from the first sweep. Neighbouring files model the violation, so "match the file you're in" is the wrong instruction.
- **An agent file created during a run cannot be spawned by name in that run** — the registry is read at session start, so a new critic or doer is unreachable until the next session. Paste its job definition into the brief and spawn a read-only agent that already exists.
- **Inject any pitfall a file has already been bitten by into the brief** — a trap commented in the file is not a trap in the brief. A brief that adds a `UTextBlock` states the project's typeface rule, or the run comes out bold.
- **Dictate the `Describe` a new leaf goes under, not only its title** - the full path is its permanent name, and an agent files it under whatever Describe it was reading.
- **A restructure's comment sweep starts at the TYPE that defines the thing being changed, not at the call sites.** A brief listing every site that reads a fact will still miss the struct whose own comment asserts it, and that one is the load-bearing definition every later reader trusts.
- The real boundary between ui-implementer and presentation-implementer is the TRIGGER (player-initiated vs event-log-reactive), not the widget type.
- **Naming an existing predicate for a brief to reuse: check what question it ANSWERS, not what it composes.** Two close questions over one state machine are two functions, each saying what it answers and what its neighbour does not.
