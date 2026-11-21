# Measuring frame rate, GPU cost and detail

## Detail

- Sharpness is detail energy - the variance of a 4-neighbour Laplacian over a fixed crop. Keep an untouched crop in frame as the control.
- **Is a surface blurry or aliased? Compare its rendered crop's Laplacian variance against a correct Lanczos resample of the source art at the size it actually draws.** Below the ideal is blur, far above it is aliasing — and aliasing reads as HIGH detail, so the number alone lies about which you have.
- **`r.MipMapLODBias -N` is the free sweep for any "should this be sharper?" question**, but it is GLOBAL: keep an untouched crop in frame as the control, and remember the fix is always a per-material `TMVM_MipBias`. Where `-N` and `-(N+2)` read identical you have hit mip 0; where the sweep does nothing at all, the texture has no mip chain.

## Which lever actually moves it

- **`sg.AntiAliasingQuality` means different things on different rungs** - on a TSR rung it is the history buffer and a modest detail cut; on an FXAA rung only `r.FXAA.Quality` is live and the difference is small. **`r.AntiAliasingMethod` is the big lever**: TSR can be most of the GPU frame, and it is what leaves a just-uncovered surface soft while it rebuilds.
- **UE 5.8 renders a desktop game BELOW native by default and TSR-upscales, harder the bigger the screen** (`r.ScreenPercentage.Default.Desktop.Mode = BasedOnDisplayResolution`). `sg.ResolutionQuality=0` is a documented no-op and not the lever; `r.ScreenPercentage` is.

## Traps

- **A Steam Deck cannot be uncapped.** Its compositor presents at the display refresh whatever `r.VSync` says, so the frame rate reads exactly 60.0 with half the frame going spare. Judge it on the game/render/GPU stage times, never on the frame delta alone.
- **GPU ms is only true uncapped.** Behind a cap the GPU downclocks to suit the work, so the same work reads slower the lower the cap. Which stage is slowest stays true either way.
- **Typing `sg.<Group> <n>` at the console pins that cvar to Console priority for the rest of the session**, and every later `Scalability::SetQualityLevels` silently leaves it there. Sweep rungs through an exec that calls `SetQualityLevels`; a console `sg.` override makes every reading after the first one a reading of the wrong settings.
- **A Slate panel over a scene that keeps rendering does not reset TSR history**, so opening and closing one is not a disocclusion and cannot be used to test one.
