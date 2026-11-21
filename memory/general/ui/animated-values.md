# Seeding, advancing and re-targeting an animated value

Per-tick syncs in general are `per-tick-sync.md`.

- An animated widget whose owner advances its own value unconditionally must never drop a step while busy — settle the in-flight tween and continue, never early-return. A "callers only ever do X while settled" comment expires the first time a raw-input caller appears.
- **"Do I still need to move?" is answered from where you were last SENT** — the outstanding target if a move is in flight, else the settled pose. A decoration-proof *tracked position* still answers the wrong question: with a move outstanding, a request for the pose you currently occupy reads as a no-op and the earlier target survives, so you glide somewhere nobody asked for.
- **Removing interpolation noise exposes gaps the noise was papering over.** A spec that fails only once you snap exactly onto the target is telling the truth — fix the guard, not the spec.
- **Re-preparing an object must not re-seed its animated values.** A seed written unconditionally in a re-run prepare snaps the animated value back for a frame. Seed on the first preparation only.
- **A render-only lag is seeded from where the thing is DRAWN, never from where its owner was last sent.** Read the owner's transform and a second placement mid-travel throws away however far the drawn part had got, while merely re-stating the placement it is already easing toward jerks it the rest of the way home.
- **A monotonic generation running ahead of the last one handled IS the pending state** — it stays open across every tick the animation is still playing, so a second "pending" flag beside it is redundant and is one more thing owing a reset on every exit path. Reset it where the thing it counts is rebuilt.
- **A widget that animates only one step at a time is walked for a bigger change**, one step per tick, leaving on ARRIVAL rather than on "not animating" - a walk that has not started yet is not animating either.
