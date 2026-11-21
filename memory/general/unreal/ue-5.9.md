# Unreal 5.9

What differs from the 5.8 notes in `mcp-audit.md`, `mcp-patterns.md` and `mcp-reaching.md`. Everything those
files say still holds on 5.9 except what is here.

## Engine and build

- The 5.9 MegaJam Preview's CompatibleChangelist is 0: every Preview update, and every switch between a 5.8 and a 5.9 checkout, is a full rebuild; 5.9 binaries do not load in 5.8. Same toolchain as 5.8.
- The MCP settings class moved: its section is `[/Script/ModelContextProtocol.ModelContextProtocolSettings]` (the old `ModelContextProtocolEngine` one still works through a redirect but warns in every build).
- **Every cook fails on 5.9** with `ToolsetManifestSeed/_Generated_/... imports class /Script/ToolsetRegistry.ToolsetRegistryManifest, which is in a module that is not available`: the editor's toolset registry adds its manifest seed to every cook. Never-cook `/ToolsetRegistry/ToolsetManifestSeed` in `DefaultGame.ini`; never-cooking the plugin root `/ToolsetRegistry` instead trips an ensure (path registered for two domains).
- Headless `MaterialEditingLibrary.recompile_material` fails without a renderer: pass `-AllowCommandletRendering` to `run-ue-python.ps1` for any script that compiles a material. The first such run shader-compiles for minutes and logs non-fatal `NiagaraRibbonVertexFactory.ush ... error X3000`.

## MCP

- Meta-tools: `list_toolsets`, `describe_toolsets {toolset_names:[..], include_schemas}` (what `ue_mcp.py describe` calls; output ~150 KB, grep a file), `describe_tools {tool_names:[..]}`, `call_tool`.
- **The Python `editor_toolset.toolsets.*` toolsets are gone.** C++ `EditorToolset.<X>Toolset` replace them (Level, Actor, Asset, Object, Material, MaterialInstance, Texture, EditorApp); logs are `ConsoleToolset.LogsToolset`. `call_tool` takes the BARE PascalCase tool name (`GetCurrentLevel`, not dotted, not snake_case); arguments are camelCase, and a wrong field errors with the valid list.
- Verified shapes:
  - Level: `LoadLevel{levelPath}`, `GetCurrentLevel{}`, `CreateLevel{levelPath}`, `AddToSceneFromClass{actorType:{refPath:"/Script/Engine.StaticMeshActor"},name,xform:{translation{x,y,z},rotation{pitch,yaw,roll},scale3D{x,y,z}}}`, `AddToSceneFromAsset{assetPath,name,xform}`, `RemoveFromScene{actor:{refPath}}`, `FindActors{filter:{name?,tag?,actorType?}}` (name matches the label).
  - Actor: `GetActorTransform{actor}`, `SetActorTransform{actor,translation,rotation,scale}`, `SetLabel`/`GetLabel{actor,label}`, `AddTag`/`GetTags{actor,tag}`.
  - Object: `GetProperties{instance:{refPath},properties:[..]}`, `SetProperties{instance,values:"<JSON string>"}`, `ListProperties{instance,root?,nameFilter?,maxDepth?}`.
  - Asset: `SaveAsset{assetPath}` — one asset per call, no batch save; `Delete{path}`, `Exists{path}`, `IsDirty{assetPath}`, `FindAssets{filter:{folderPath,bRecursive}}`, `GetReferencers{assetPath}`.
  - Material (full object paths): `CreateMaterial{folderPath,assetName}`, `AddExpression{materialOrFunction,expressionClass:{refPath},x,y}`, `ConnectExpressions{fromExpression,fromOutputName,toExpression,toInputName}`, `ConnectToOutput{expression,outputName,materialProperty:"MP_BaseColor"}`, `GetExpressionInputs`, `Recompile{materialOrFunction}`.
  - MaterialInstance: `Create{folderPath,assetName,parent:{refPath}}`, `ListParameters{material}`, `SetScalarParameter{instance,name,value}`, `SetVectorParameter{instance,name,value:{r,g,b,a}}`.
  - Texture: `ImportFile{folderPath,assetName,sourceFile,bReplaceExisting?}`, `GetSize{texture:{refPath}}`.
  - EditorApp: `StartPIE{options:{bSimulate,playMode:"PlayMode_InViewPort",warmupSeconds}}`, `IsPIERunning`, `StopPIE`, `CaptureEditorImage{}`, `CaptureAssetImage{assetPath}` — images arrive as an MCP image content item.
  - Logs: `GetLogEntries{logCategory?,pattern?,maxEntries?}`. Automation: `RunTests{testNames:[exact]}` blocks and returns results.
- A call made while the editor runs a slow task answers `Not run: the Unreal Editor is running a slow task` and changes nothing — retry it. `Delete` can answer null and leave the asset; check `Exists` and the disk, delete once more.
- SlateInspector `Click` on a game TEXT ref can be refused (an overlay border owns the point; `LastRefusal` says which); click the page's umg widget ref to focus instead.

## Fab (`FabToolset.FabToolset`)

- `SearchFabListings{Keywords,bFreeOnly,AssetFormats,ListingTypes,Count}`, `SearchFabMyLibrary{Count,SortBy:"newest"}`, `GetFabListingDetails{ListingId}`, `InstallFabListing{ListingId,AssetFormat,EngineVersion,DistributionMethod,Title}` with the option's fields passed unchanged; `FabSignIn` opens a browser — the owner signs in, never an agent. Fields are PascalCase here.
- Install answers `handed-to-editor` and the asset lands under `Content/<Title-ish folder>/` within seconds; delete it with `AssetToolset.Delete` on the folder and compare `git status --porcelain --ignored` before and after. A Fab asset is never committed.
- **Nothing reports WHICH Epic account is signed in** — not the tools, not the log. Ask the owner to confirm in the editor's Fab window (Window → Get Content → Fab) before treating a library listing as theirs.
- A fresh account refuses every download with `You must accept the Fab EULA` until the owner accepts it on fab.com, and an empty library answers `results: []` with no error — neither proves anything.
