# Packaging a build

- **Building proves nothing about a package.** JSON read through `FPaths` is not UE content, so nothing cooks it and nothing stages it without a `RuntimeDependencies` declaration; and a plugin enabled in the `.uproject` ships unless it carries `"TargetAllowList": ["Editor"]`. Neither shows in a build log — check the produced staging tree.
- **The cook follows references only, so anything reached by NAME never cooks** — a level opened by name, a material resolved from a slug. Maps go in `MapsToCook`; `DirectoriesToAlwaysCook` covers the rest and does NOT pick up maps.
- **UE stages a launcher shim at the tree root with Epic's own version resource**, named after the project, and never restamps it. A recursive `*.exe` search finds it first and reports Epic as the maker while passing. `-nobootstrapexe` drops it; check the game's own binary under `<Project>/Binaries/Win64`.
- **UBT expands a `RuntimeDependencies` `...` wildcard into the target's cached `Makefile.bin`, and a new file under that tree never invalidates it** — so a new data file silently fails to ship. Delete the makefile before packaging and compare the staged data trees with the repo by hash.
- `UnrealPak <staged>.utoc -List` is the only view of what actually shipped — a file listing shows one `.ucas` blob.
- **The engine caps no texture** (`BaseDeviceProfiles.ini`: `TEXTUREGROUP_World MaxLODSize=16384`), so an 8K scan ships at 8K unless the asset carries its own `MaxTextureSize`. That is a cook-time ceiling — source art is untouched, so raising one costs only a repackage.
- `-nodebuginfo` drops the `.pdb` but not `d3d12SDKLayers.dll`, which stages as an ordinary file beside `D3D12Core.dll`.
