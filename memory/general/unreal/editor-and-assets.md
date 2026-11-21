# UE editor, assets and levels

Call shapes are in `mcp-patterns.md`; importing and saving assets in `asset-import.md`, material graphs in
`materials.md`, fonts in `fonts.md`, driving PIE in `pie-console.md`; what counts as visual evidence in
`../workflow/visual-acceptance.md`. This file is the policy: whose editor it is and what the level owns.

## The editor is the owner's, not yours

- **Never start, stop or kill the editor from an agent.** If a build fails because the editor holds the DLLs, report BLOCKED and wait — an agent cannot know whether that process is a stray or the owner's live PIE session, and the costs are wildly asymmetric. Write this into every brief positively; "the editor must stay stopped" reads as permission to stop it.
- While the owner says they are using the editor, run nothing that builds — `build-game.ps1` relinks the module DLLs the live editor holds.
- **Leave the editor down at the end of a run.** A responding editor may be the user's own — re-ask per instance, never carry an earlier "safe to stop" forward.
- Live Coding (Ctrl+Alt+F11) is the iteration path for C++ and needs no restart, but it never re-runs file-scope/static const OBJECT initializers and cannot patch layout or reflection changes, and a header edit (even a constant) does not reach the .cpp files including it — a hand tester on Live Coding needs a full build to see header changes. Hand-tuned values belong on instance `UPROPERTY`s. It is iteration only; the gate is a clean full build.

## Scripts and assets

- Shared scripts exist; never hand-roll the transport: `scripts/ue_mcp.py`, `scripts/ue-editor.ps1`, `scripts/run-ue-python.ps1` (always with `-SuccessPattern` — raw exit codes are polluted by unrelated log errors). Keep reusable editor-Python in one folder, check it before writing a script, and promote reusable one-offs there.
- `run-ue-python.ps1 -Script` needs an ABSOLUTE path, and `-ScriptArgs` takes ONE space-separated string that cannot contain a space inside a value (UE strips the quotes before splitting, so `"Patua One"` arrives as two argv entries). Parametrise by pre-setting globals in a tiny driver file that `exec()`s the real script.
- Never create a `UMaterialInstanceDynamic` in an actor constructor; the CDO's MID breaks level save. Create lazily, guarded by `!HasAnyFlags(RF_ClassDefaultObject)`.


## Levels

- The LEVEL is the placement authority, not any spec's pinned table — read placed transforms from the level's committed textual dump.
  - **Before editing a level, check the dump can SHOW the edit.** It recorded transforms only until a material swap produced a zero-line diff — a binary commit whose paired text proved nothing. Extend the dump script in the same task rather than committing an invisible change.
- Deleting anything from the level requires grepping the specs for its name first; a spec may pin level contents by exact label.
- **To decide whether a CoreRedirect is still NEEDED, scan the assets' own bytes** — `.uasset`/`.umap`/`.png` are LFS-tracked, so `git grep` reads a ~130-byte pointer and always answers clean. Control-test the scan first against a string you know is in the file (`/Script/`, the module name) before trusting a zero, and scope a whole-repo sweep to `git ls-files`: a filesystem walk drags in thousands of stale hits from `.audit/`, `Saved/`, `Intermediate/**/*.rsp.old` and `__pycache__/`.
  - The same scan answers "may I DELETE this asset" without starting an editor for `get_referencers` — read the files from disk, not through git: one LFS type can smudge to real bytes while another stays a ~140-byte pointer, so the control test is what tells you which you got. Sweep the repo's TEXT files for the name separately: `.dump.json` sidecars cite each other in prose, and deleting an asset strands every citation.
- To flush a CoreRedirect out of a level (a renamed class or package), load and resave it, refusing if any actor came back a stub rather than a real class — a blind resave bakes that damage in. Regenerate the paired `.dump.json` after; an unchanged manifest is the proof nothing else moved.
- UnrealEditor rewrites `Config/DefaultInput.ini` with engine-default boilerplate on every run — re-clean after the last UE invocation of the run, before committing.
