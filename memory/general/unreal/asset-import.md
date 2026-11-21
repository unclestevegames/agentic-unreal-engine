# Importing, saving and deleting assets

What silently does not happen when a texture or other asset is imported, re-imported, saved or deleted,
and how its `.dump.json` sidecar is written. Call shapes are `mcp-patterns.md`.

## Importing textures

- **Import textures through `unreal.TextureFactory`, never Interchange** — Interchange names its factory nodes after the ABSOLUTE source path and serialises those names into the asset, so moving the clone strands the old directory name inside every texture imported that way. Re-importing through `TextureFactory` clears assets that already have one.
- **A fresh import RESETS every setting to factory defaults** — compression, texture group, mips, address mode, streaming. Capture them first and re-apply and re-read all of them after each run; nothing warns when they vanish.
- **Check the project's texture-import mip default.** Under `TMGS_NoMipmaps` a large source drawn small must be set to `TMGS_SimpleAverage` explicitly after `import_file` or it crawls — never `TMGS_FromTextureGroup` on `TEXTUREGROUP_UI`, whose engine LOD group is itself NoMipmaps. The import's own read-back is the only tell.
- Small UI icon textures import as `TC_EditorIcon` + `TEXTUREGROUP_UI`, not a world texture's `TC_Default`/`TEXTUREGROUP_World` — block compression shreds small glyph edges. Mipmaps off only because those sources are already small; a large source drawn tiny keeps them on, or minification crawls.
- **UE builds mips by averaging RGBA per channel, never premultiplied** — whatever colour sits UNDER a transparent pixel is dragged into every smaller mip, so art exported with a black surround grows a muddy fringe wherever it is drawn small. Fix at the source by flooding the artwork's own colour outward under the transparent pixels, leaving alpha untouched.
- **Texture re-import over an EXISTING asset**: `import_file` refuses the name outright, and `AssetTools.delete` no-ops while a live CDO references the texture. Headless (editor stopped) is the easy route — `unreal.AssetImportTask` + `TextureFactory` with `replace_existing=True` keeps the asset GUID so C++ `FObjectFinder` paths keep resolving. With the editor LIVE, run the same task through its own Cmd console instead.
- **Every table-driven import script re-imports every row in its list**, so adding one row rewrites all the others' `.uasset` with identical settings even from unchanged sources. Revert the rows you did not mean to change before committing.

- **No headless tool reads a texture's mip count** — Python has no property, and under `run-tests.ps1` `GetNumMips()` and the platform data read 0 for every texture. Prove mips by reading back `mip_gen_settings` plus a power-of-two size. The non-power-of-two setting is `power_of_two_mode` = `unreal.TexturePowerOfTwoSetting.STRETCH_TO_POWER_OF_TWO`; streaming off is `never_stream`.
- **An older revision of an LFS source PNG**: `git show <rev>:<png>` gives the pointer and `git lfs smudge` refused it; copy `.git/lfs/objects/<oid[0:2]>/<oid[2:4]>/<oid>` (oid from the pointer) instead. Saves time.

## The `.dump.json` sidecar

- **A Texture2D's sidecar is HAND-AUTHORED JSON** (`asset`/`class`/`note`/`sourceFile`/`dimensions`/`content`/`import`/`consumer`/`provenance`) — `dump_asset.py` on a `Texture2D` exports raw PNG bytes onto the `.dump.json` name. Copy a sibling's sidecar and edit it; the import settings actually applied are what make it reviewable. Material sidecars are hand-authored for a different reason — see `materials.md`.
  - A sidecar generated from the asset reads `asset_import_data.get_first_filename()` for the source path and `blueprint_get_size_x/y()` for size (works headless; `imported_size` is not exposed to Python).

## Saving and deleting

- MCP-authored assets are not durable until `AssetTools.save_assets`, and a SEPARATE headless process cannot see them until then (it reads from disk, not the live session). `FObjectFinder` statics also cache a "not found" for the rest of the process — save, then RESTART before placing instances that reference the new asset.
- **`AssetTools.save_assets` fails with a misleading `Asset does not exist: <path>` while PIE is running**, for every asset. `StopPIE` first. Parameter writes during PIE succeed, so the edits are real and merely unsaved.
- **A save issued from a headless `run-ue-python.ps1` against an asset the LIVE editor holds returns `True` and does nothing** — the live process holds the `.uasset` open and `SavePackage` gives up on the sharing violation. Tell: mtime and byte size unchanged. Headless alongside a live editor is safe for READS only.
- **A headless write can land on DISK and still leave the editor's in-memory copy stale** — `ObjectTools.get_properties` still reads the old value, and that value wins at the next save. Verify through the live editor's own read-back, never by mtime.
- **`AssetTools.delete` can return `true` and delete nothing** — the file is still on disk and `AssetTools.exists` still answers `true`. Check both; `get_referencers` answering `[]` is what makes removing the files by hand safe. It never removes the hand-authored `.dump.json` sidecar — `git rm` that separately, then grep the repo for the asset's name, since dumps cite each other in prose.
