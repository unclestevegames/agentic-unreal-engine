# Git operations that lose or misplace work

## Uncommitted work

- `git add -N` new files before snapshotting a diff for critics — but `git checkout --` truncates an `add -N` file to zero bytes, and on a modified-unstaged file discards the entire uncommitted task diff (silently, leaving a valid older file that can even test green). Capture `git hash-object` before any mutation; prefer mutating against a committed baseline.
- **`git stash pop` can apply only part of a stash and still leave the entry**. Copy the actual files aside (not only a patch) before stashing, restore from the copies, and prove it by regenerating the diff and hashing it against the saved patch.

## Submodules

- **A `git switch -c` lands inside the SUBMODULE when the shell is standing in it** - the Bash tool's working directory persists across calls, so one `cd` into a submodule makes the next branch operation create the issue branch there and check out its `main`. Use `git -C` for every submodule read, run `git submodule status` after every branch operation, and `git branch --show-current` before every commit.

## Digests

- **`git hash-object <file>` runs the file through the filters of whatever repo the shell is STANDING in**, so hashing a file outside the repo answers for bytes it never read - two identical files hash differently and nothing says why. Pass `--no-filters` whenever the point is the bytes themselves.
- **Where `core.autocrlf` is true, a git blob and the working-tree file NEVER digest the same** Anything that deploys a repo file and then compares the two must read the blob (`git cat-file blob <ref>:<path>`) at both ends, or it finds every file "behind" forever. From PS 5.1 read it via `ProcessStartInfo` + `StandardOutput.BaseStream.CopyTo` - `>` and `$(...)` both re-encode.
- **`git show HEAD:<path>` is LF; the working file is CRLF.** Normalise CRLF to LF before deciding which lines or blank runs are new, or an edit "restoring" HEAD's shape rewrites pre-existing lines.
