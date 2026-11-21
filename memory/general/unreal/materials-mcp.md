# Editing a material graph through MCP `MaterialTools`

The commandlet route in `materials.md` is preferred and owns the rules both routes share.

- `list_expression_classes {"material_or_function":{refPath},"search":"<substring>"}` → `add_expression {..,"expression_class":{refPath},"x":int,"y":int}` returns the new node's refPath → `get_expression_input_names {"expression":{refPath}}` to discover pin names → `connect_expressions {"from_expression":{refPath},"from_output_name":"","to_expression":{refPath},"to_input_name":"<pin>"}` → configure node fields via `ObjectTools.set_properties` → `recompile {"material_or_function":{refPath}}` → `AssetTools.save_assets` IMMEDIATELY.
- **Every `MaterialTools` call wants the FULL object path** (`/Game/Materials/M_Foo.M_Foo`); the bare package path is rejected.
- **Wiring to the MATERIAL ROOT** is `connect_to_output {"expression":{refPath},"output_name":"","material_property":"MP_BaseColor"}` — `connect_expressions` rejects the material's own refPath. Read back with `get_property_input`, whose material field is `material`, NOT `material_or_function` — the one call in the toolset that breaks the sibling convention.
- `get_expression_inputs` requires **both** `material_or_function` and `expression`; it returns every wired input as `[{expression, output_name, input_name}]`. `get_expressions` lists every node, which is how you prove you left nothing orphaned.
- **`connect_expressions`/`connect_to_output`/`recompile` return `{"returnValue": null}` on SUCCESS** — success is the absence of an error string; don't misread null as failure.
- **`MaterialTools.delete_expression` reliably CRASHES the editor** (3 for 3, across sessions, never on add/connect/recompile/save). Never call it - delete through the commandlet route's scratch-copy surgery in `materials.md` (its `delete_material_expression` also crashes on an asset loaded from disk). Save immediately after wiring the NEW graph either way, so a failure costs only the cleanup.
