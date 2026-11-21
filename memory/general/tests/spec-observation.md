# What an assertion reads

Whether a `ForTest` accessor, a getter, a derived index or an oracle can see the thing it is asked about.
The wider list of assertions that prove nothing is `spec-assertions.md`.

## Accessors

- Assert the RENDERED state, not the intent flag — `IsShown()` means "I asked for it"; the tween's alpha decides where it draws.
- A `ForTest` accessor that RECOMPUTES a value is a second copy of the production expression, not an observation. Read what the widget actually applied.
- **An accessor that SORTS cannot see a reorder inside what it sorts** — a display order sorted by kind hides a push, so a spec proving the push moved nothing there passes with the clamp deleted. Assert the raw membership, which is where things physically stand.
- **Indexing one derived accessor by another off the same source is true by construction** — a display order indexed by a highlight index names the selected item whether or not anything works. Assert through the path that actually CONSUMES the index (what the press named).
- **A getter that reads a material parameter answers the PARENT's default when the instance never set it** - so a spec asserting a pushed value passes with the push deleted, whenever that value equals the material's own preview default. Ask for the overridden value only, and check the brush is actually drawing through that material.
- **A position accessor with a default answer cannot see "not drawn at all"** — one answering `Top` for a widget whose parent is null let no spec see a header block dropped from every row. Assert the widget is PARENTED when the subject is whether it is on screen.
- **An accessor that clamps is an accessor a spec cannot fail on.** A highlight index that clamps `INDEX_NONE` to 0 reports slot 0 with nothing selected. Assert through the presenter's raw index when the thing under test is "is anything selected at all".
- **A `...VisibleForTest` accessor must answer what is DRAWN, not what the data says** - one reading a row's own flag passes while the mark it names is never parented. Name the accessor after the player's eyes and make it check both halves.

## Oracles

- An oracle must be independent of the CODE, not of the DATA. Build it by a different code path over the same live source; a frozen copy is a content pin wearing a contract's clothes, and every legitimate edit becomes a failure.
- **A texture's own imported pixels are readable in a spec** — `Texture->Source.GetMipData(Out, 0)` under `WITH_EDITORONLY_DATA`, after asserting `GetFormat() == TSF_BGRA8`, since the channel order decides whether the scan sees anything. Prove the read discriminates by widening its threshold until the count matches an independent scan of the committed source PNG.
- A helper in a spec's anonymous namespace cannot fail a test, so its error paths return empty strings that `Contains()` tolerates. Check the oracle at the call site for every entry.
