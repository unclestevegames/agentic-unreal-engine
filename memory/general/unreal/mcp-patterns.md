# Verified MCP Call Patterns

Exact, live-verified call shapes for UE 5.8's MCP server; WHAT the tooling can do at all is
`mcp-audit.md`. Schemas are frozen per engine install — re-verify only on engine update, `.uproject`
plugin-list change, or a custom project toolset.

Starting, stopping and talking to the server is `mcp-reaching.md`. Task detail lives beside its task: importing, saving and deleting assets `asset-import.md`, material
graphs `materials.md`, font import `fonts.md`, capturing the running game `capture.md`, an inspectable
editor and driving PIE `pie-console.md`.

## Verified call shapes

| Operation | Toolset / tool | Args (exact) |
| :--- | :--- | :--- |
| Find actors by tag | `editor_toolset.toolsets.scene.SceneTools` / `find_actors` | `{"name":"","tag":"<Tag>","collision_channels":[]}` — ALL THREE required; returns `returnValue: [{refPath}]` |
| Load level | same / `load_level` | `{"level_path":"/Game/Maps/<Level>"}` |
| **Create a NEW level — no native tool exists** | an editor-Python script | `scripts\run-ue-python.ps1 -Project <uproject> -Script <abs script> -ScriptArgs "/Game/Path/LevelName"` with a `-SuccessPattern` the script logs — make it idempotent, and it is safe alongside a live editor |
| Place an actor | same / `add_to_scene_from_class`, `add_to_scene_from_asset` | `{"actor_type":{"refPath":"/Script/Engine.StaticMeshActor"},"name":"X","xform":{"location":{x,y,z},"rotation":{pitch,yaw,roll},"scale":{x,y,z}}}`; from asset `{"asset_path":"/Engine/BasicShapes/Cube.Cube","name","xform"}` → `returnValue.refPath`. `set_actor_transform` is `{"actor":{refPath},"xform":{...},"worldspace":true}` |
| Run ONE automation leaf (never the suite) | `AutomationTestToolset.AutomationTestToolset` / `RunTests` | `{"testNames":["<full test path>"]}` blocks and returns the summary. It focuses the Message Log tab, so a following `StartPIE` shows no game panel in Snapshot until the level's tab is `Click`ed |
| Delete a probe LEVEL asset | `AssetTools` / `delete` | returns `true` but leaves the `.umap` while that level is loaded — `load_level` another map first |
| Delete a placed ACTOR (not a content asset) | same / `remove_from_scene` | `{"actor":{"refPath":"<full actor path>"}}` → `true`; then `save_assets` the level |
| Read object/component props | `editor_toolset.toolsets.object.ObjectTools` / `get_properties` | `{"instance":{"refPath":"<full path>"},"properties":["Prop1",...]}` → `{"returnValue":"<JSON string>"}`. NOT `object`/`property_names`. Component path = `<actorRefPath>.<ComponentName>`; actor path = `/Game/Maps/<Level>.<Level>:PersistentLevel.<ActorName>`. Works for plain asset properties too |
| Write props | same / `set_properties` | `{"instance":{"refPath":"<full path>"},"values":"<JSON-ENCODED STRING of the property map>"}` — `values` is a STRING, not a nested object. For actor components, force `OnConstruction` afterwards via `set_actor_transform` (same values) and READ BACK |
| Set an asset-REFERENCE property | same / `set_properties` | the refPath value MUST repeat the asset name after the dot: `/Game/Materials/M_Foo.M_Foo`. A bare package path is silently rejected ("not a valid object path") |
| Actor transform get/set, labels, tags | `editor_toolset.toolsets.actor.ActorTools` | round-trip verified. **`set_actor_transform` does NOT honour "unset fields = don't change" for `scale`** — passing only `location` silently reset a `(300,300,1)` scale to `(1,1,1)`. Always pass the full transform |
| Save assets/level | `editor_toolset.toolsets.asset.AssetTools` / `save_assets` | `{"asset_paths":["/Game/Maps/<Level>", ...]}` — ALWAYS before an editor stop |
| Delete an asset | same / `delete` | `{"path":"/Game/Path/Asset"}` — `path`, singular; `asset_paths` is only `save_assets`' field |
| Rename/move a level asset while it is loaded | same / `move` | silently returns `false`, even after loading a different map. Workaround: `duplicate` to the new path, `delete` the old, `save_assets` the new |
| Texture: import | `editor_toolset.toolsets.texture.TextureTools` / `import_file` | `{"folder_path":"/Game/Textures","asset_name":"T_Icon_Foo","source_file":"<abs path>"}` → `returnValue` is a LIST even for one import. Field is `source_file`, not `file_path` |
| Texture: pixel dimensions | same / `get_size` | `{"texture":{"refPath":"<full path>"}}` → `{"returnValue":{"x":int,"y":int}}` |
| Create a material / a material instance | `MaterialTools` / `create_material`; `MaterialInstanceTools` / `create` | the instance's parent is a `parent` ref. Graph editing after creation: `materials.md` |
| Material instance params | `editor_toolset.toolsets.material_instance.MaterialInstanceTools` / `set_scalar_parameter` etc. | field is `name`, not `parameter_name`. Correctly REJECTS a parameter the material does not define — real semantics, self-documenting error |
| Read a MATERIAL's own parameter defaults | `MaterialTools/get_expressions` then `ObjectTools/get_properties` per expression | `get_expressions {"material_or_function":{"refPath":"/Game/Materials/M_Foo.M_Foo"}}` → `[{refPath}]`; then `{"instance":{"refPath":"<expr refPath>"},"properties":["ParameterName","DefaultValue"]}`. **`get_properties` fails the WHOLE call if any named property is absent on that class**, so ask a `TextureSampleParameter2D` for `["ParameterName","Texture"]` and a scalar/vector for `["ParameterName","DefaultValue"]` — never one list for both. `"properties": []` returns `{}`, not everything |
| PIE control | `EditorToolset.EditorAppToolset` / `StartPIE`,`StopPIE`,`IsPIERunning` | StartPIE: `{"options":{"bSimulate":false,"playMode":"PlayMode_InViewPort","warmupSeconds":2}}`; StopPIE: `{}` |
| Asset thumbnail capture | same / `CaptureAssetImage` | `{"assetPath":"/Game/Path/Asset"}` → base64 PNG. Acceptance evidence ONLY for content-only work with no in-game render path yet — grep for consumption first, else game-view capture stays mandatory |
| Editor-viewport capture (ITERATION ONLY, never acceptance) | same / `CaptureViewport` | needs an explicit `captureTransform` or you get stale frames, AND `"annotations":[]` — that field has no default and omitting it errors |
| Editor logs | `EditorToolset.LogsToolset` / `GetLogEntries` | `category` DEFAULTS to `"LogsToolset"` if omitted (not "all") and `pattern` must be NON-EMPTY — omit either and you get `Log category 'LogsToolset' not found.` Field is `maxEntries`, camelCase. Reading `Saved\Logs\<Project>.log` is a fine fallback for a single-process drive, never when two headless runs overlap |
| Slate / game UI | `SlateInspectorToolset.SlateInspectorToolset` / `Observe`,`Snapshot`,`Click`,`PressKey`,`Type`,`Screenshot` | Observe `{"ref":"<r>","maxDepth":40}` → Snapshot same args returns a text tree with `[ref=xN]`; Click `{"ref":"xN"}`; PressKey `{"key":"Gamepad_FaceButton_Bottom"}` (atomic, no holds); Screenshot `{"ref":"<r>"}` → base64 PNG in the TEXT content item, not an image item (`ue_mcp.py`'s `extract_png()` handles it). **Refs are PER-SESSION** — rediscover after any restart. Drive recipes: `pie-console.md` |
