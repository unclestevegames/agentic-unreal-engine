# Importing a font

Every face shown on both a 3D label and a UMG panel is TWO assets, `F_X` and `F_X_Offline`, and that is
engine-forced: `UTextRenderComponent` refuses a runtime-cached font and draws nothing silently, while an
offline font has no typeface entries so UMG cannot reach italic or bold through one. Assert
`FontCacheType` where it matters — the wrong one of a near-identically-named pair is invisible until the
label is blank.

## Runtime font (UMG) — needs a LIVE editor

- **`unreal.FontFileImportFactory` CANNOT run headless.** It touches the Slate application and dies with `Assertion failed: CurrentApplication.IsValid()`, killing the commandlet, regardless of `batch_create_font_asset`. Route it through the live editor's Cmd console (transport detail in `mcp-reaching.md`). Once the assets exist, dump/export works fine headless — the constraint is specific to the import call.
- **A FontFace's `SourceFilename` is a COOKED property**, so the absolute path it was imported from ships inside the player's `.ucas`. Move or rename the clone and every face carries the old location into the build; repoint them all at the current one with a script.
- Writing any FontFace property headlessly needs `set_editor_property(..., unreal.PropertyAccessChangeNotifyMode.NEVER)` — the default notify runs `PostEditChangeProperty`, which flushes the Slate font cache and takes the commandlet down with the same `CurrentApplication.IsValid()` assertion.
- Parametrise the import script by pre-setting its globals in the same `py` statement that `exec()`s it. The factory with `batch_create_font_asset=YES` produces TWO assets from one import — `<name>` (FontFace) and `<name>_Font` (Font, the actual `UFont` widgets bind to); rename them to `<name>_Face` / `<name>`; the rename auto-fixes `Font.CompositeFont`'s soft reference.
- **Adding a SECOND typeface (Italic, Bold) to an existing Font is a different job, and the obvious route does not work.** Import the face alone (`batch_create_font_asset=NO`), then attach it: `UFont.CompositeFont` is readable, but its nested fields are bare `UPROPERTY()` with no Edit specifier, so `get_editor_property("default_typeface")` throws and `to_dict()` shows zero keys — the Python bridge refuses non-`CPF_Edit` members. The way through is the struct's own `export_text`/`import_text` (which do not check `CPF_Edit`): read it as UE's native text, splice a `(Name="Italic",Font=(FontFaceAsset="..."))` entry into `Fonts`, `import_text` it back, `set_editor_property` the whole struct.
- **`TypefaceFontName` silently falls back to `Default` for a name the asset does not hold**, so a bad attach renders upright with nothing failing. Verify by re-dumping the asset, never by a call's return value; a spec asserts the font's own `CompositeFont.DefaultTypeface.Fonts` holds an entry by that name.

## Offline font (baked atlas, for `UTextRenderComponent`) — runs HEADLESS

- `TrueTypeFontFactory` has none of `FontFileImportFactory`'s Slate dependency, so `run-ue-python.ps1` is the route: `unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, path, unreal.Font, factory)`.
- The face comes from GDI **by name**, so register the TTF for the process first with `ctypes.windll.gdi32.AddFontResourceExW(path, 0x10 /*FR_PRIVATE*/, 0)` — nothing is installed on the machine.
- **GDI SILENTLY SUBSTITUTES a face it does not know**: the import succeeds, produces a full glyph set, and saves the wrong typeface with nothing logged. Prove the face took by importing a control against a deliberately unregistered name and requiring the two `Ascent`s to differ; `EmScale` is identical across faces at one `Height` and discriminates nothing.
- **The page size defaults to 512x256 and must be raised with the bake height** — a height-96 bake at the default spreads 220 glyphs over 26+ atlas pages (1024x1024 fits it in 2). Pass `TEXTURE_PAGE_WIDTH`/`TEXTURE_PAGE_MAX_HEIGHT`, and check the baked `texture_index` spread, not just that the import succeeded.
- Each bake runs ~5 min and baking a control face first doubles it, so budget ~10 min per font — and it holds the game module DLL, so no build can link while it runs.
- A font-import option's bool is exposed with the leading `b` STRIPPED (`use_distance_field_alpha`), and `UFont.Textures` is protected, so an offline font cannot be hand-built from Python — that factory or nothing. Building options needs `FontImportOptions.get_editor_property("data")` → mutate → `set_editor_property("data", ...)` (a value copy); reading them back off a `UFont` returns the struct directly with no `data` indirection.

## Sourcing a static TTF

- **`google/fonts` doesn't always carry a static per-weight TTF** — some families ship ONLY a variable font. To get a genuine static named instance, use the CSS2 API with a legacy user-agent to force `format('truetype')` rather than woff2: `curl -A "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/534.34 (KHTML, like Gecko) PhantomJS/1.9.0 (development) Safari/534.34" "https://fonts.googleapis.com/css2?family=<Family+Name>:wght@400"` → the `src: url(...) format('truetype')` line points at a `fonts.gstatic.com` static instance.
- **Verify the download by parsing the TTF's own `name` table, never the filename** — read Family / Subfamily / PostScript / `fsType` (0 = installable embedding, which is what shipping inside a game needs) / absence of `fvar` (a genuine static). `strings` finds nothing (name records are UTF-16BE) and `file` doesn't surface them either.
