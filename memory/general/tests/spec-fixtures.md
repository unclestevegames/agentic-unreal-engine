# Getting a fixture to the state the spec is about

What a fixture costs. One that answers to the machine it runs on is `spec-machine-coupling.md`.

## Fixtures

- **Never hard-code a value the owner tunes by eye** — read the tunable back for the magnitude and pin what a developer gets wrong instead (the axis, the order, the even spacing), plus bounds that hold at any value. A spec that pins the number turns the suite red on the first retune, for no defect.
  - **A private constant with no accessor is what FORCES specs to repeat its literal** — give it a static getter beside the others and the repetition stops being the only option. Grep assertion MESSAGES for the number too (`raised (+10)`), not just the expressions, since a `BaseZ + 10.0` hides from a search for the composed vector.
- **A fixture that clears its threshold by a hair is one metrics change from proving nothing while still reading green.** Pick the side with headroom and say why at the fixture.
- **A callback a spec hands to production must not close over a leaf LOCAL** — production parks it somewhere that outlives the leaf, so a leaf failing before the callback fires leaves a live reference to a destroyed stack frame and the next call crashes the whole run. Put the record on the spec class.
- **A spec that bypasses the engine code which normally CLEARS an engine-global static must clear it itself** — the whole suite is one process. `FScreenshotRequest::RequestScreenshot` is only ever reset by `UGameViewportClient::ProcessScreenShots`, which a headless spec never reaches, so the spec calls `FScreenshotRequest::Reset()`.
- A fixture that manufactures state by driving the engine in a way no player can is a liability the day the engine changes. Prefer a state the player really reaches — usually simpler and it does not expire.
- Before rebuilding a fixture that can no longer reach its state, ask what the spec uniquely proves. Decompose before you rebuild; the residue often already lives elsewhere.
- **Walking a menu by counting D-pad presses is a fixture assumption** - one inserted row breaks every such walk. Ask for the row BY KIND, and test a clamp by overshooting the live row count, never by a press count that happens to overshoot today.
- **A fixture that sets a value AFTER the setup production sets it before is describing a state the game never reaches.** The repair is to give the fixture the value, not to gate the production derivation.
- **A widget spec needing a live world must build the widget with `NewObject<T>(World)`, never `GetTransientPackage()`** — otherwise `GetWorld()` does not resolve through the outer chain and the widget's own `TActorIterator` lookups find none of the spawned actors. Tear down with `GEngine->DestroyWorldContext` + `World->DestroyWorld(false)` in `AfterEach`, or worlds and timers leak across specs in the same headless process.
- A fixed tick count is a fixture assumption about a step machine's length — adding one step anywhere breaks every one of them. The repair is the bounded settle on the asserted condition, never a bigger delta.
- **A bounded wait that falls out with no assertion is a lie with a budget** — the spec then measures a scene still in motion and can pass by luck. Bound it in simulated SECONDS (call sites tick at different step sizes, so a tick count means nothing across them).
