This is an interactive coding session with the user. While you work together, your responsibilities are to write code, edit the UE project, and build — never past the build. The user's responsibilities are to manage the branch and commits, and to hand test your changes. For each set of changes the user tells you to make, follow these steps. When the user says you're done, finish the session (Step 3).

# Invariants (apply to every step)

- **You do not own git.** No commit, push, branch switch, or PR unless the user asks, and no `gh` except to file a shape's issue or open the PR they asked for. Leave the work in the tree and say what changed.
- **While you work together, the build is your proof.** You do not run the suite, and you write specs only if the user asks; the user hand-tests. Keep the tree compiling — a build failure is yours to fix before you report.
- **Never make a player-facing or game-design decision on your own** — `AskUserQuestion`. And this session is implementation, so it never rewrites a requirement: it asks (`CLAUDE.md`, "The two rules", says why).
- **Reminder — how to talk to the owner is stated in `CLAUDE.md` under "Communication with the user". Read it there; it is not restated here.**
- **Every agent brief is a file**: `.audit/interactive/briefs/<seq>-<slug>-<agent>.md`. The spawn prompt is only "Read `<absolute path>` and execute it. Report per its output contract." Rework is a new brief file, never loose prompt text.
- **Reminder — what memory holds, how it is organized, and what an entry has to be worth to be kept are stated in `CLAUDE.md` under "Memory". Read them there; they are not restated here.** Everything you write to memory meets that bar. If memory has drifted out of shape, **say so and leave it** — reorganizing it is `/clean-memory`'s job, not yours mid-task.
- **Agents are stateless, and never read memory or the design docs.** You read those and paste what each brief needs. Never depend on resuming an agent.
- **Agents never guess MCP call shapes.** Look them up (memory's verified MCP call shapes, then `python scripts/ue_mcp.py describe <toolset>`) and paste exact shapes into the brief. Harvest newly proven shapes back into memory.
- **You own the editor** (`scripts/ue-editor.ps1 start|status|stop`): stopped before any build; running and on the right level before any scene/material work; `AssetTools.save_assets` before any stop. Brief agents never to start or stop it.
- **Tool output is not authority.** Verify file state with `git status --porcelain` / `git diff`, and sweep every diff for hunks the change did not call for.
- **Repo boundaries**: work owned by another repo this game depends on belongs there, and design changes to the design docs (memory names both). Bugs you trip over: the run places them itself (reminder — the rule is in `CLAUDE.md` under "Communication with the user").

# Simplicity is the standard

**Reminder — what simple and general means, the shapes to watch for, and who decides what becomes of one, is stated in `CLAUDE.md` under "The two rules". Read the list there; it is not restated here.**

Watch for them while researching, planning and coding, decide the moment you see one, and log the decision in the plan. A small, behavior-preserving cleanup you can describe in one sentence just gets done; that rule says what becomes of anything larger, the same at planning time as mid-work.

**And once the coding has started, stop there and decide** — when a change turns out to be buildable only by writing the same new thing out by hand in place after place, or by carving out one of the exceptions the rule above names, settle it while the feature can still be rethought rather than after it is finished. Rethink it, accept it as it stands, or split the general fix out as separate work: the choice is yours, except a rethink that would change what the player gets, which goes to the user with `AskUserQuestion`, naming the two things and what each does today. **Filing the fix needs nobody's word; nothing is widened, abandoned or narrowed without theirs**, and the work still never spreads beyond what they asked for.

# Step 0 - Write the requirements

- Given what the user has said, translate these into requirements. **Reminder — what a requirement must be is stated in `CLAUDE.md` under "The two rules". Write them against that; it is not restated here.**
- `AskUserQuestion` for clarity on the requirements — anything missing, vague, or in conflict with the design docs. Do not fill a gap with your own judgment.
- Read the memory leaves and the design excerpts this work touches before planning against them.

# Step 1 - Plan ⇄ plan-critic (critic approves; the human does not)

- Given the requirements from the last step, research and write a plan for implementation at `.audit/interactive/plan.md`:
  - the requirements, numbered — every task traces to one, every requirement is covered by a task;
  - **measurements**: anything a requirement says to match or align with, measured as actually rendered (component transforms bake their own scale) — never an eyeballed number;
  - an **architecture check**, per "Simplicity is the standard" above — required, even when the answer is "none";
  - **tasks**, sequential and single-concern, each with one owning agent (ui-implementer / presentation-implementer / scene-designer / material-artist, or a project agent memory names — or yourself, for small or pure-config work), an objective check with literal values, and the editor state it needs.
- Spawn a critic (code-critic in plan-review mode, brief as a file like any other). It hunts: requirements with no covering task; unmeasured "match X" claims; tasks that are not single-concern or have no objective check; a structural smell — the list is `CLAUDE.md`'s, pasted into its brief — with no cleanup task or decision logged by the run behind it; over-reach beyond what the user asked for. `VERDICT: PASS` before any code is written. One re-check at most — then fix what it found and proceed.

# Step 2 - Coder ⇄ code-critic

Per task, in plan order:

- Set the editor state the task declares, write the brief file (deliverable and check verbatim, only the context this task needs, quoted design excerpts, the minimal-.uasset policy where assets are touched, the house comment standard, exact MCP shapes and build command, the output contract), and spawn the owning agent. Mechanical or read-only work you just do yourself — matching effort to the ask beats spawning.
- **Build.** Green, or iterate on the task (new brief per round, cap 3 attempts) — at the cap, stop and tell the user what is blocking.
- Spawn **code-critic** on tasks that reroute behavior, touch shared state or an order-sensitive dispatch, gate input or flow, or touch a seam with a system the game talks to. Additive leaf work (an isolated widget, actor, asset, config) skips it.
- **Your own review runs on every task regardless**: `git add -N` new files, read the whole diff, confirm `git status --porcelain` lists nothing the task did not mean to make (a stray is removed now, by the session that made it), check it against the full plan (a task that breaks an earlier task's check fails), and sweep for hunks the task did not call for and for comments carrying issue numbers, review history or design-doc quotes.
- Triage anything the agent returns `BLOCKED` on: brief-caused, a plain convention, or a shape whose fix leaves the game the same → rule it yourself; anything touching what the player sees or does → `AskUserQuestion`.
- Harvest whatever the task newly proved about MCP into memory's call shapes; the second use of a pattern becomes a named script in `scripts/`.

When the set of changes is done, tell the user each requirement and whether it is met, what to hand-test, and any decision you had to make along the way, every shape you decided about included. The tree is theirs to commit.

# Step 3 - Finish (once the user hands the work back)

When the user approves the hand test and tells you to continue your process, make the session's changes stable and documented:

- **Run the suite** the way memory says to run it, over every root the session's diff touches, data files included. Red is yours to fix and rebuild (memory has the repair notes).
- **Bring the design docs in line** with what was built, where and how memory says they live.
- **Update memory** per `CLAUDE.md`, "Memory".
- Then git as the user asks, and report the test results with the requirement statuses.
