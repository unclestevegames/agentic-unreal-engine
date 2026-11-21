# Folding checks into shared hosts

- A host keeps its enclosing `Describe`'s prefix, so a case pulled in from a sibling `Describe` sits under a path that mislabels it — put a cross-`Describe` host at the common parent (or the spec root) with a title naming every case.
- Folding every case out of a `Describe` leaves an empty shell whose leading comment now describes nothing — delete the shell and carry the comment above the first case's `AddInfo`.
- Draft each host title from the full list of its case titles; a placeholder or a title covering only some cases is the commonest rejection.
- Cases under a mutating `BeforeEach` fold only with a hoisted per-case set-up/tear-down called inside the host before each case.
- After a fold, run by root prefixes plus each new host's own root, never by a list of full paths: a `-Filter` of ~16 KB hangs the editor at start-up with no report.
