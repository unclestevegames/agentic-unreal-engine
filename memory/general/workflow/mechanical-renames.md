# Renaming a token or a word across many files

Scripted edits in general are `windows-shell.md`.

- **For a mechanical token rename, substitute at the BYTE level** (`open(f,'rb')` → `bytes.replace`): an ASCII token cannot touch a non-ASCII byte, a BOM or a line ending, which is what makes it safe where a whole-file rewrite is not. Assert the substitution count against a measured census, then `git diff --numstat`.
  - **Prove it was ONLY a rename in one command**: apply the rename map to BOTH sides of the diff (idempotent on the renamed side) and compare the line multisets. What is left is the finding.
  - **A slash-led command name also matches inside a PATH** (`/review-performance` in `.audit/review-performance/<date>/`) - re-grep the paths the rename must leave alone after substituting.
  - **Census by camelCase-segmented WORD, never by stem** — a stem matches inside other words (`realis` in `realistic`). A word table finds only the spellings it has rows for (`travelling`, `colourless`), so sweep again by SUBSTRING afterwards and judge the residue.
  - **The damage lands in PROSE, not in code.** Two shapes: a comment where both words already appeared comes out doubled ("per-zone zone"), and one where the word meant the other thing comes out false. Re-read every changed comment; the compiler and the suite see neither.
  - **A literal that is FROZEN HISTORY is excluded from every rename** — an old save file's keys, an older wire version's names. Renaming them stops the code recognising the files it exists to convert.
  - A quoted-literal pass still hits strings that are not the thing being renamed: `Contains(TEXT("terrains"))` was a substring of a diagnostic message, not a wire key. And a wire key lives in a spec tree in TWO byte forms, raw `"key"` and escaped `\"key\"` — a pattern for one cannot match the other.
- **A member moved into a sub-struct is respelled from the COMPILER's error list, never by text** - its name collides with other structs' members. Parse `error C2039: 'X': is not a member of 'Old'` at `file(line,col)`, insert the qualifier at that column, loop the build (MSVC stops a file at 100 errors); prove it by stripping the qualifier from both diff sides. A build log written by PS 5.1 `Tee-Object` is UTF-16 - decode it first or the parse finds nothing.
