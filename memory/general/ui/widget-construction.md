# Building a widget's tree

All UI is programmatic C++ — no Widget Blueprints. Sizing, positioning and type are in
`widget-layout.md`; textures, paintings and rich text are `widget-images.md`; what a per-tick sync
decides to show is `per-tick-sync.md`.

## Construction

- Align widgets against each other with slot alignment, never a computed font-metric offset. `FSlateFontMeasure::GetBaseline` is the font's DESCENDER (negative), and reading it as "height above the baseline" pushes content down by a whole line.

- Build the `WidgetTree` in `NativeOnInitialized()`, never `NativeConstruct()`. `AddToViewport()` bakes the Slate widget from `RootWidget` first, so the widget renders empty forever while `SetVisibility()` on children "succeeds".
- **A widget that must outlive a level change belongs to the game instance and re-adds ITSELF, from the same per-tick reconcile that decides whether it is wanted.** The object survives the travel; the viewport it was drawn on does not, and creating it early puts nothing on screen. Gate the add on `IsInViewport()` - the viewport's own answer is the state, never a "have I done this" flag - and let that one reconcile own the creation too, so no caller can reach the level without it.
- **A widget whose visibility comes from an apply-only-what-changed sync must still be collapsed at
  construction.** The first sync sees nothing changed and writes nothing, so the widget keeps a fresh
  widget's visible default and draws forever.
- **Every widget derives from one base class whose `Initialize()` runs `NativeOnInitialized()`** when the engine skipped it for want of a player context. One deriving from `UUserWidget` directly builds nothing headless. A spec builds one with `NewObject` + `Initialize()`, plus `AddToRoot()`/`RemoveFromRoot()` around the spec lifetime.
- A headless widget's state read before `Initialize()`, or straight after it, passes by construction: setters no-op without the tree, and the build writes the default. Build the tree first, then assert each read against the opposite of the state just before the call.
- **A child built via `WidgetTree->ConstructWidget<T>()` is fully built before the call returns**, in a game and headless alike, so a field its `NativeOnInitialized` reads must be its own default - a host writing it after construction is too late (a thumb height written that way drew half its sizes from the old value). `WidgetTree` is null on a bare `NewObject` widget until `Initialize()`, so a public setter reachable there must check it.
- **A host that shows sub-screens must forward `AdvanceTime` to whichever one is open**, or the first sub-screen with a tween or a hold gesture silently never ticks.
- **A page FRAME stays out of the input path.** A frame (background + one content + prompt bar) is a plain `UUserWidget` and the controller routes commands to the CONTENT, so the shared hold-to-repeat gesture arms on the widget that owns the commands. A frame that forwarded input would arm the gesture on itself, and every nested screen's own `ReleaseDirectionRepeat()` would then release an unarmed copy. Each content therefore owns its own `NativeTick` -> `AdvanceTime`, and the frame advances none of them.
- **Anything that scrolls to keep an item in view is ONE shared scroll-list widget** - the host gives it orientation, a per-item measure, gap and room; never a hand-built clipped box plus offset.

## Calls that silently do nothing

- `UImage::SetDesiredSizeOverride()` before Slate exists (i.e. any construction-time code) — there is no backing property to reapply. Wrap the image in its own `USizeBox` instead.
- `UBorder::SetHorizontalAlignment`/`SetVerticalAlignment` before Slate construction — centre via a `UCanvasPanelSlot` with point anchors and alignment instead.
- `SetAutoWrapText(true)` alone, whenever no ancestor constrains the width: it converges on "wrap at my own natural single-line width". Give an explicit `SetWrapTextAt`.
- `UPanelWidget::InsertChildAt` does not reorder a live panel — it appends to the real Slate children and reorders only UMG's `Slots`, which is exactly what `GetChildAt` reads, so the natural spec passes while nothing moved on screen. Fill one grow-only pool in read order so child order is structural.
- `SetColorAndOpacity` on a UserWidget whose glyphs are nested UserWidgets renders it INVISIBLE, not tinted. Pulse a plain `UTextBlock`/`UImage` instead.
