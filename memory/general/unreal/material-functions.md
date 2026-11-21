# Authoring a material FUNCTION headless

Same commandlet route as `materials.md`; these are the function-only call shapes (proven).

- Create: `AssetToolsHelpers.get_asset_tools().create_asset(name, dir, unreal.MaterialFunction, unreal.MaterialFunctionFactoryNew())`; nodes via `lib.create_material_expression_in_function(func, cls, x, y)`; `lib.connect_material_expressions` works inside it; finish with `lib.update_material_function(func, None)` then `save_asset`.
- Read back: `lib.get_material_function_expressions(f)`, `lib.get_inputs_for_material_function_expression(f, e)`.
- `FunctionInput`: `input_name`, `input_type` (`unreal.FunctionInputType.FUNCTION_INPUT_VECTOR2` / `_SCALAR`), `sort_priority`. `preview_value` cannot be set from Python (no Vector4 conversion) - leave it; only the function's own preview goes blank.
- `FunctionOutput`: `output_name`. Calling it from a material: `MaterialExpressionMaterialFunctionCall` + `.set_material_function(f)`; its pins are the input/output names; `.get_editor_property("material_function")` reads it back.
- `MaterialExpressionIf` pins: `"A"`, `"B"`, `"A > B"`, `"A == B"`, `"A < B"`. Wiring both `==` and `<` to the unchanged sample keeps a count-1 path bit-identical rather than a zero-weight blend.
- `MaterialExpressionSaturate` takes the unnamed pin `""`; a `Constant`'s value is `r`.
- **Rebuilding a function's graph DISCONNECTS every caller's inputs** - the new `FunctionInput` nodes are new objects, so each `MaterialFunctionCall` comes back with its pins `None`. Reconnect each call's inputs in the same script and read them back.
- **Measure a function by RENDERING it, headless**: `run-ue-python.ps1 -AllowCommandletRendering`; a world from `unreal.EditorLoadingAndSavingUtils.new_blank_map(False)`; `RenderingLibrary.create_render_target2d(world, 1000, 3, RTF_RGBA32F)`; a scratch Unlit probe material calling the function, `MaterialLibrary.create_dynamic_material_instance(world, mat)` + `set_scalar_parameter_value`; `draw_material_to_render_target(world, rt, mid)`; `read_render_target_raw_uv(world, rt, u, v)` returns float colour. Use an ODD row count so the middle row is the true mid-height.
