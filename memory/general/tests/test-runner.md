# Running the suite

- Always run through `scripts/run-tests.ps1` (headless, `-nullrhi`). The native-MCP `RunTestsByFilter` path drives a real GPU and crashes the full suite with D3D12 device-removed.
- Gate on `TOTAL` + `failed=0` + `notRun=0` + `succeededWithWarnings=0`. The suite runs warning-free, so any warning is a new one worth reading — a spec whose own subject IS a logged warning declares it with `AddExpectedMessagePlain`, which asserts it instead of hiding it.
- **Predict the expected TOTAL before every targeted run and treat a shortfall as a filter bug.** Filters fail open: a typo runs fewer tests, prints ALL PASS, and exits 0.
- A filter matching ZERO tests is a critical error to UE, not an empty run — it never writes `index.json` and `run-tests.ps1` reports `FAIL - no index.json produced`, which reads like a hang. Confirm a root is gone by that plus `No automation tests matched` in the log, never by expecting `TOTAL=0`.
- **A root added to a `+`-joined filter that does not move the TOTAL matched nothing** - that is the only tell, since the run still says ALL PASS. Confirm the file's own `GetBeautifiedTestName()` before naming a root for it - and a nested `Describe` carries its parent's prefix, so the "obvious" root-level form matches nothing.
- A filter is a PREFIX, so a root name that prefixes a sibling sweeps both in — `Root.Foo` also runs `Root.FooBar`. Predict off prefixes, not off the root's own leaf count.
- Count a root's leaves off a REPORT's own `fullTestPath` list, never by grepping `It(` in the file: a nested `Describe` and a helper-only `Describe` both break the correspondence.
  - Count by the EXACT prefix string the filter will carry, not by a tidy grouping of the path, or every task reports a shortfall and re-investigates a filter that was fine.
- **A PR's stated TOTAL can be stale or one behind what `main` actually runs** — measure `origin/main` itself (detach, build, run: a few minutes; rebuild the branch afterwards, or the built game is main's) and diff the leaf NAME sets: identical sets is the claim worth making, and it names the leaf when they differ. Reconcile any two TOTALs this way, never by counts - "off by one" and "a spec silently vanished" read the same.
- `-ReportPath` must be ABSOLUTE, or the tests run fine, the log says it exported, and the script reports "no index.json produced".
- `index.json` is UTF-8 **with BOM** — read with `encoding="utf-8-sig"`; walk each node's own `tests` array for leaf names rather than trusting the counts.
- `-IncludeSlow` appends a global slow root to the filter rather than scoping slow leaves to the roots you named, so naming one slow root sweeps in every slow spec in the module. Leave it OFF a per-task filter entirely, or the predicted count is wrong for a reason that reads like a missing leaf.
- **A worktree builds and tests itself** — the cheap way to baseline an older commit: `git worktree add --detach .worktrees/<name> <commit>`, `git -C <wt> submodule update --init`, then the worktree's OWN `scripts\build-game.ps1` and `scripts\run-tests.ps1` (its `run-tests: project=` line names the tree it ran). Build one tree at a time: a single build can already near a dev box's memory limit.

## Filters

- Spec-file names do not predict roots — read the file's `BEGIN_DEFINE_SPEC` line, or a hand-written spec base's own `GetBeautifiedTestName()` override.
- Derive the filter from `git diff --name-only`, not from the feature's name — every spec file touched contributes its root.
  - **And a touched DATA file contributes the root of whatever spec pins it**, which no diff over `Tests/` will show.
- **A spec that sweeps every widget CDO for a property** contributes its root whenever a widget gains one, whatever the feature is called.
- Every PRODUCTION file touched contributes its root too — an exhaustive sweep over an enum lives under whatever root owns it, not the feature's.
- When a task edits a production file that a whole ROOT exercises, filter by the ROOT, not by a Describe prefix. A Describe prefix is narrower than the file, which is how a regression survives several commits.

## Build evidence

- **`run-tests.ps1` does NOT build.** Run `build-game.ps1` first, every time, or the run answers for the previous binary — a TOTAL that misses your own new specs is the only tell.
- **Never chain a build and a test run in one shell command.** A filter that greps the build output SUCCEEDS when it finds error lines, so `&&` runs the tests anyway - against the previous binary, reporting ALL PASS. Run the build, read its verdict, then run the tests as a separate command.
- Never truncate `build-game.ps1`'s output above its `Result:` line: a failed build is invisible behind `Select-Object -Last 2`, and the run that follows reports ALL PASS for the previous binary.
- **`build-game.ps1` is an ordinary incremental build and reports `Target is up to date` as success**, so an unsaved edit compiles nothing, says OK, and the suite answers for the old binary: read the action list, not just the `OK` line, whenever you expect a compile. For gate evidence delete `Intermediate/Build` and `Binaries/` (plus the plugin's own), confirm a nonzero action count, and run the human's actual entry point.
- **A cold build can die at exit `-1073741819` mid-link with no compile error** — the build log shows `UbaSessionServer - Killed process ... Low on memory`. Re-run `build-game.ps1`: it resumes and succeeds; it is the machine, not the code.
- **A Shipping build is affordable evidence, not a last resort** — `Build.bat <Game> Win64 Shipping -Project=<abs .uproject> -WaitMutex`, minutes cold and about one incremental. It is the decisive check that a `#if !UE_BUILD_SHIPPING` body is genuinely absent from the shipped game.
- Reverting a mutation with a backdated `Copy-Item` restores the old mtime, UBT skips the rebuild, and the mutant binary survives a clean `git status`. Revert with `git checkout --` and confirm the DLL mtime actually moved.
