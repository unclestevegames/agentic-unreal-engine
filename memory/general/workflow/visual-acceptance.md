# What counts as visual acceptance

What a capture can and cannot show, and what counts as evidence. Capturing the running game is
`../unreal/capture.md`.

- **Anything whose value only the real environment can produce — what the platform layer answers, what a device reports — is invisible to every spec, and the visual pass is the only thing that can catch it wrong.** A seam that lets specs SET that value cannot also prove the live lookup reads it correctly. Spend the pass whenever a screen shows a value the suite can only fake.
- **The editor viewport differs from the game in lighting, exposure, camera and serialized editor-session MIDs.** For a NEW camera pose, do the ITERATION in real PIE too: a geometric estimate cannot account for props whose bounds it does not know.
- Judge a layout round holistically, as if seeing the frame fresh: spacing, alignment and relative sizing of everything, not just the item the user named. And verify the specific claimed change is actually visible.
- Grade and tint requirements are ordinal claims about the OUTPUT of an unknown-gain pipeline — sample the settled game view (average a patch per surface and assert the stated ordering), never read the authored parameter.
- A proportional decoration can be entirely invisible because the ends of the extent it is a fraction of sit inside something else. A geometry spec that pins the container cannot see whether the thing inside it is visible — compare the element's visible reach against the real on-screen footprint, in the state the player actually views it in.
- **A change to a shared view must be judged in ordinary play, not only in the feature that prompted it.** A camera change verified against one scripted state shipped a worse framing for ordinary play, because that state was the only one anyone looked at.
