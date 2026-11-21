# What the UE 5.8 tooling can do

Capability matrix — WHAT is reachable. Exactly HOW to call it is `mcp-patterns.md`. Everything here was
exercised live on this machine, not read off a vendor claim.

## How the tooling works

- Official plugin: `Engine/Plugins/Experimental/ModelContextProtocol` (+ `ToolsetRegistry`, `EngineAssetDefinitions`, `Experimental/Toolsets/AllToolsets`). Enable all four by listing them in the `.uproject` — no editor UI needed.
- Server: HTTP JSON-RPC (Streamable HTTP) at `127.0.0.1:8000/mcp`. **Does not auto-start** unless configured, but that is scriptable — `Config/DefaultEditorPerProjectUserSettings.ini`:
  ```
  [/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]
  bAutoStartServer=True
  ServerPortNumber=8000
  ServerUrlPath=/mcp
  bEnableToolSearch=True
  ```
- With `bEnableToolSearch=True` (default), `tools/list` exposes only 3 meta-tools: `list_toolsets`, `describe_toolset`, `call_tool`. Real tools go through `call_tool{toolset_name, tool_name, arguments}`, where `toolset_name` is the dotted name from `list_toolsets` (e.g. `editor_toolset.toolsets.scene.SceneTools` — mixed Python/C++ naming conventions). `describe_toolset` gives exact schemas; **guessed field names fail**, but errors echo the full expected schema, so a wrong guess costs one round-trip, not a dead end.
- ~40 toolsets are registered, far more than the surface a game needs (Niagara, Sequencer, GAS, StateTree, PCG are present but out of scope).

## Coverage matrix

| Capability | Verified tool(s) | Status |
| :--- | :--- | :--- |
| Level: load | `SceneTools.load_level` | verified |
| Level: create new | *(no native tool)* → an editor-Python script via `run-ue-python.ps1`; runs concurrently with a live editor (~1.1s) | verified (fallback only) |
| Level: save | `AssetTools.save_assets(["/Game/Level"])` — generic asset save covers it | verified |
| Actor: place from class/asset | `SceneTools.add_to_scene_from_class` / `add_to_scene_from_asset` | verified |
| Actor: transform get/set | `ActorTools.get_actor_transform` / `set_actor_transform` | verified — exact round-trip |
| Actor: label/tags, find/enumerate | `ActorTools.set_label`/`get_label`; `SceneTools.find_actors` | verified |
| Actor: delete from level | `SceneTools.remove_from_scene` | verified |
| Object: generic property read/write | `ObjectTools.list_properties` / `get_properties` / `set_properties` | verified |
| Material: create, add expression, wire, recompile | `MaterialTools.*` | verified — but `delete_expression` CRASHES the editor; see `materials.md` |
| Material graph without MCP | `unreal.MaterialEditingLibrary` via `run-ue-python.ps1` | verified — preferred route |
| Material instance: create, set scalar/vector/texture param | `MaterialInstanceTools.*` | verified — correctly rejects undefined parameter names |
| Texture: import with explicit settings | `TextureTools.import_file`; re-import over an existing asset via `AssetImportTask(replace_existing=True)` | verified |
| Font: import | `FontFileImportFactory` (live editor only) / `TrueTypeFontFactory` (headless) | verified — see `fonts.md` |
| Automation: discover/list/run/results | `AutomationTestToolset.*` | verified, but **do not use for the suite** — it drives a real GPU and crashes on device-removed. `scripts/run-tests.ps1` is the gate runner |
| PIE: start/stop/status | `EditorAppToolset.StartPIE`/`StopPIE`/`IsPIERunning` | verified |
| PIE/editor: screenshot | `EditorAppToolset.CaptureEditorImage` / `CaptureAssetImage` — inline base64 PNG, no file round-trip | verified |
| Log: tail/filter | `LogsToolset.GetLogEntries` | verified |
| C++ compile loop | `Build.bat <Project>Editor Win64 Development` | verified — fresh ~36s, incremental ~7s; standard `file(line,col): error Cxxxx` |
| Slate / running-game UI: inspect + drive | `SlateInspectorToolset.Snapshot`/`Observe`/`Click`/`PressKey`/`Type`/`Screenshot` | verified — deep Snapshot exposes running-game UMG text with refs; PressKey is atomic (no holds), so hold gestures go through the game's own exec hooks. Recipes: `pie-console.md` |

## Not covered

- Third-party MCP servers (UAIP, StraySpark, chongdashu/unreal-mcp) were never evaluated — the official plugin plus the Python fallback covered every capability needed, so no gap justified it.
