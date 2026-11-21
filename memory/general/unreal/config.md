# Config values that never arrive

Why a value written in `Config/*.ini` does not reach the running game. Both of these fail silently -
no warning, no error, and the value simply is not what was written.

- **A `//` in an unquoted ini value starts a comment.** `Endpoint=https://host/path` reads back as
  `https:`. Quote the whole value (`Endpoint="https://host/path"`); Unreal strips the quotes on read.
  Quote base64 too - it may grow a `/` the next time it is rolled.
- **A truncated value beats a good compiled-in fallback**, because a fallback only fires on empty.
  Prefer one source for a value over a config-plus-default pair.
- **`UInputSettings` config lives in `Config/DefaultInput.ini`, not `DefaultEngine.ini`**
  (`UCLASS(config=Input)`). Mappings in the wrong file never register.
- Anything read via `GConfig` in a **Shipping** build has no log to check - Shipping compiles logging
  out unless the target asks for it. Write what a value resolved to into the diagnostic log instead.
