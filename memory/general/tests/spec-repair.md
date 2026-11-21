# A red suite, and naming a spec so it can be run

Attributing failures and repairing them, plus the naming and file-scope rules a spec has to obey to be
targetable at all. Running the suite and choosing a filter are `test-runner.md`.

## Judging and repairing a red suite

- Attribute every failure to its assertion text before repairing any: the grouping tells you whether you are looking at one cause or ten.
- A failure naming a "sanity" or "precondition" check means the fixture moved, not that the product broke.
- A spec that pins a bug as its PRECONDITION blocks the fix and reads green right up until you fix it. Rewrite with the expectation flipped and retitle; do not delete. The same holds when a behaviour is deliberately REVERSED: the spec that pinned the old rule is the natural guard for the new one, and deleting it loses the only leaf that would notice the reversal being undone.
- **A fixture that performs by hand what the product is about to do itself breaks as a SUBMIT or COUNT failure, not as an assertion about the rule** — three families walked the cursor between two picks of one question, and once the game landed it there the walk overshot onto an item nothing offered, so the press after it named nothing. Delete the manual step and assert the landing in its place; the leaf then guards the new rule.
- When a behaviour is removed, disposition each affected spec on its own: whole-subject specs are rewritten, specs where the behaviour was incidental are NARROWED. Deleting a narrowable one loses a real rule.
- When a curation pass deletes a spec for its FIXTURE, the subject it proved needs re-homing, not deleting — usually by extracting the decision as a pure function.
- A narrower filter can report MORE failures than the full suite; that is real information about fixture coupling, not a measurement error. The gate is the full suite.
- **A leaf green on its own and red in the full suite is a BOUND answering to load, not a flake to re-run.** The tell is a settle whose budget is ticks while the thing it waits for lands on another thread - 600 ticks at a millisecond of sleep each is about six tenths of a second, plenty idle and not always enough under load. Bound the live-engine half by wall clock instead, generously, so the only way left to fail is the game never doing it.

## House rules

- File-scope names in an anonymous namespace must be unique across the module. Adaptive unity build makes duplicates an ODR error under SOME groupings only, so a green build is not evidence — prefix per file or make the helper function-local.
- Filter punctuation, three different failures: a comma truncates the command silently, an apostrophe fails loudly with no report at all, and both together can run 10+ minutes producing nothing. A spec-title guard, where the project has one, refuses them.
- **`-Filter` takes `+`-joined prefixes (one run can cover two roots), so a `+` inside a `Describe`/`It` title makes that leaf untargetable**: UE splits the filter argument on literal `+`, tearing the path in two so it matches nothing. A title guard may not gate this — the widest `+`-free prefix is as narrow as you can get.
- **Make the SHARED fixture the discriminating case rather than adding a leaf beside it.** Making the shared fixture exercise the new case made four existing leaves see the new rule, and deleted the need for the new leaf entirely - a family that would have grown shrank back to its own size.
- **Census a block of wire fixtures by CONSTANT NAME, never by line number** — adjacent refusal fixtures differ only by which key each omits, so a line-numbered list pairs each with its neighbour's reason and drops one entirely.
- **Hunt the duplicate by the FIXTURE'S SHAPE, not the feature's name** — grep the whole Tests tree for the degenerate value itself (an empty destination list, a zero count, a null owner). The spec already proving your fact usually sits under an unrelated root, so a search by subject misses it.
- Leave `#include`s alone when fanning out deletions — an unused include costs nothing, and a removed one breaks a sibling that still needed it.
- A `Describe` with helpers but no `It` registers nothing and reads as coverage for years. Grep for one whenever a TOTAL undershoots a naive `It(` count.
- A title census that greps `(Describe|It)\(TEXT\("` reads as ZERO — titles are often written bare, `It("...")`.
- **Register an `AddExpectedMessagePlain` BEFORE the first call that can emit the message, and measure its count from a run's own log.** A message logged before the filter is registered leaks through uncaught and lands as an unexpected warning, which the gate fails on even with nothing red.
