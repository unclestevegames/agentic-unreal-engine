# Authoring a material graph

Two routes reach the same graph. **Prefer the commandlet** — it does everything MCP's `MaterialTools`
does, needs no live editor, and carries no `delete_expression` crash risk. The MCP route is
`materials-mcp.md`; call shapes for everything else (properties, assets, textures) are in
`mcp-patterns.md`.

## Route 1 — `scripts/run-ue-python.ps1` (preferred)

- `lib = unreal.MaterialEditingLibrary`; `lib.get_material_expressions(mat)` (creation order, NOT graph order — the index says nothing about dataflow); `lib.create_material_expression(mat, unreal.MaterialExpressionDotProduct, x, y)`; `lib.connect_material_expressions(from, "", to, "A")` and `lib.connect_material_property(...)` (both return **bool** — check every call); `lib.recompile_material(mat)`; `unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)`. Paths need the `.Name` suffix.
- **`unreal.MaterialProperty`'s Python members are SCREAMING_SNAKE** - `MP_BASE_COLOR`, `MP_AMBIENT_OCCLUSION`, never `MP_BaseColor`. And **`get_material_property_input_node(mat, MP_MAX)` kills the commandlet outright** - no exception, no log line, the process just ends. Never iterate `dir(unreal.MaterialProperty)`; name the properties you want.
- The library also has `disconnect_material_property`, `disconnect_material_expressions` and `clear_all_material_instance_parameters`, all headless - so unwiring an output and stripping an instance back to its parent need no MCP and carry no crash risk.
- **Read an instance's OWN overrides** (not the parent's defaults) off `mi.get_editor_property("scalar_parameter_values" | "vector_parameter_values" | "texture_parameter_values")`, then per entry `.get_editor_property("parameter_info").get_editor_property("name")` and `("parameter_value")`. That is the only view that distinguishes "this instance sets it" from "it inherits it".
- **A raw pin read fails** (`get_editor_property("input"/"a"/"b")` → "protected and cannot be read") and `unreal.MaterialExporterT3D` is not bound, so there is no textual export to diff. Two library calls DO read the graph back: `lib.get_material_property_input_node(material, property)` for what feeds a material output, `lib.get_inputs_for_material_expression(material, expression)` for what feeds a node's pins.
- **Address an existing node by `expr.get_name()`** (`"MaterialExpressionMultiply_2"`) after a `get_material_expressions` walk — never by editor position (an orphan can sit at the exact x/y of its live counterpart), never by array index, and never by the `.dump.json`'s node names (hand-authored, they drift from the live `MaterialExpression*_N` numbering). Identify a node to wire onto by class + `parameter_name` + its own inputs.
- **Expression property names are NOT discoverable from Python** — `dir()` lists only specially-exposed attributes, so the snake_case UPROPERTY names a new node needs are invisible, and a wrongly-built graph cannot be deleted. Build a scratch material under `/Game/Temp`, probe there, delete it, then touch the real asset. Proven names:

| Node | Fields |
| :--- | :--- |
| `MaterialExpressionFresnel` | `exponent`, `base_reflect_fraction` |
| `MaterialExpressionLinearInterpolate` | `const_a`, `const_b`, `const_alpha` |
| `MaterialExpressionSmoothStep` | `const_min`, `const_max` |
| `MaterialExpressionConstant2Vector` | `r`, `g` |
| `MaterialExpressionConstant3Vector` | `constant` |
| `MaterialExpressionComponentMask` | `r`, `g`, `b`, `a` (bools) |
| `MaterialExpressionDivide` / `Multiply` / `Add` | `const_a`, `const_b` |
| `MaterialExpressionTextureSampleParameter2D` | `texture`, `group`; UV pin is `"UVs"` |
| any `*Parameter` | `parameter_name`, `default_value`, `group` |

- A node's canvas position is `material_expression_editor_x` / `_y` — needed to place a new node clear of the existing graph; guessing the name does not error, it silently overlaps.
- `get_inputs_for_material_expression` pads its list with `None` for every unconnected pin, so membership tests need a `None` guard.
- **A texture sample's `Bias` pin does not exist until `mip_value_mode` is `TMVM_MIP_BIAS`** — set the mode, then connect. A bias only chooses among mips that EXIST, so on a `TMGS_NoMipmaps` texture it silently does nothing.

## Either route

- **A rewire's orphans cannot always just be left.** A `TextureSampleParameter2D` holds its default texture as a HARD package reference, so a sample left feeding nothing still pins that texture and nothing can delete it. Prune by REACHABILITY - walk back from every wired material output and delete what the walk never reaches - never by a hand-written list, so the script cannot remove something still doing a job. The script's root list of outputs is the whole safety assumption and needs revisiting whenever a material gains one.
- **Deleting an expression from an asset LOADED FROM DISK crashes the commandlet** (`Assertion failed: !IsRooted()` from `delete_material_expression` and the function forms); the same call works on a `duplicate_asset` copy. Do the surgery on a scratch copy under `/Game/Temp`, then delete the real asset and duplicate the copy to its path, and `os.remove` the scratch `.uasset` (`delete_asset` leaves it on disk).
- **Guard a graph script against re-entry** — check for one of its own parameter names and return early. There is no reload/discard tool in `AssetTools`, so nodes added before an abort persist in memory and get saved if the run later succeeds.
- **A freshly created material defaults to `ShadingModel=MSM_DefaultLit`** — set `MSM_Unlit` explicitly if it is meant to be lighting-independent.
- A node's single unnamed pin is REPORTED as the literal string `"None"` but must be ADDRESSED as `""` (`ComponentMask`, `Abs`, `OneMinus`, `Clamp`). `MaterialExpressionDesaturation`'s main colour pin is likewise literally named `"None"`, with `Fraction` as its 0..1 blend.
- An arithmetic node's `ConstB` is consulted only when its `B` pin is unconnected — `Multiply(A=<wire>, ConstB=300.0)` is the right way to bake a literal without adding a `Constant` node.
- `output_name:""` on a `VectorParameter` resolves to `"RGB"` (alpha dropped) — same convention `TextureSampleParameter2D` uses. Its single channels connect straight through as `"R"`/`"G"` (proven), so a scalar taken off a vector parameter needs no `ComponentMask` at all.
- A `VectorParameter` is the only vector parameter type; feed a float2 pin through a `ComponentMask(RG)` of it, or the multiply fails to compile.
- A texture sampler with no UV input wired falls through to TexCoord0, which wraps the image around the whole mesh; project from `LocalPosition` masked to the face axes, and clamp. The exception is a plane whose own UVs already map to its local axes and whose orientation the actor sets — there TexCoord0 is exactly right, so say so at the node.
- **A `.dump.json` can describe a graph nobody built, and nothing complains** — a MID silently no-ops `SetScalar/VectorParameterValue` for a parameter the parent material lacks, so C++ pushing a documented-but-absent parameter looks fine for years. Read the live graph back before trusting any dump claim you are about to build on.
- **Material `.dump.json` sidecars are HAND-AUTHORED.** `AssetTools.export_assets` on a Material falls back to a glTF mesh exporter and leaves a stray nested `Content/Materials/Game/...` folder — delete that and write the JSON from the session's own read-backs. Do NOT run `dump_asset.py` for materials.
