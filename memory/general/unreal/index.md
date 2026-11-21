| Name | When to use |
| :--- | :--- |
| editor-and-assets.md | when the task needs the live editor, a level, or an asset script — whose editor it is and what the level owns |
| build.md | when a build, link or editor launch fails in a way that reads like a toolchain fault |
| mcp-audit.md | when you need to know WHETHER the UE tooling can do a thing at all — capability matrix |
| mcp-audit-runbook.md | every /mcp-audit run — how to run it (craft, not findings) |
| mcp-patterns.md | when making a UE editor/MCP call — the verified argument shape for each operation |
| mcp-reaching.md | when starting, stopping or connecting to the editor's MCP server, or sending MCP calls from a script |
| ue-5.9.md | when working with a 5.9 editor: its build, its MCP toolset and tool names (which replace `mcp-patterns.md`'s), and the Fab toolset |
| asset-import.md | when importing, re-importing, saving or deleting a texture or other asset, or writing its `.dump.json` sidecar |
| config.md | when a value written in Config/*.ini does not reach the running game |
| materials.md | when creating or rewiring a material graph |
| material-functions.md | when creating or calling a material FUNCTION headless |
| materials-mcp.md | when editing a material graph through MCP `MaterialTools` instead of the commandlet |
| fonts.md | when importing a font, adding a typeface, sourcing a static TTF, or choosing which font asset a 3D label or widget uses |
| pie-console.md | when driving PIE or the editor through SlateInspector's Cmd console |
| capture.md | when photographing what the running game draws, measuring its pixels or frames, or reading its state from the Slate tree |
| packaging.md | when packaging, cooking or measuring a shipped build |
| perf.md | when measuring frame rate, GPU cost or how sharp something draws |
