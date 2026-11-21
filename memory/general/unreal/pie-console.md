# Driving PIE or the editor through SlateInspector's Cmd console

What a `-game` drive does not need: an inspectable editor, PIE windows, and typing the game's own exec
hooks into the editor's Cmd box.

## Getting an inspectable editor

- **`scripts/ue-editor.ps1 start` is SlateInspector-BLIND** (`UnrealEditor-Cmd.exe -unattended -WindowStyle Hidden`): no window tree, no Cmd console, so the dev-exec path is unreachable. For any live drive launch `UnrealEditor.exe` yourself (`. scripts\ue-engine.ps1` then `Get-UeEngineDir`), poll `http://127.0.0.1:8000/mcp`, and write the pid to `%LOCALAPPDATA%\<Project>\ue-editor.pid` (the folder `ue-editor.ps1` names after the `.uproject`) so `ue-editor.ps1 stop` still cleans up.
- **To judge a screen at the player's own resolution, run PIE `PlayMode_InEditorFloating` and resize the window with Win32 `SetWindowPos`.** `unreal.LevelEditorPlaySettings` is not bound in Python and `r.setres` never reaches the PIE window; the game relayouts fine on the resize. In-viewport PIE is DPI-scaled to the editor's panel (1439x894 → 0.83), which moves every measured size — a layout solved there is solved for the wrong screen.
- **Every `StartPIE` makes a NEW floating window and a NEW Slate window ref** (`w3`, `w4`, `w5`…), so a `FindWindow` on the previous title returns 0 and the old ref is dead. Re-find the native window by PARTIAL title through `EnumWindows`, and re-`Snapshot` for the window ref, after every `StopPIE`/`StartPIE` cycle.

## The Cmd console

- **`PressKey`'s UE gamepad names, and which button each is**: `Gamepad_FaceButton_Bottom` = X, `Gamepad_FaceButton_Right` = Circle, `Gamepad_Special_Right` = Start, `Gamepad_DPad_Up`/`_Down`. They reach the game's action mappings; `PressKey` is atomic, so a HOLD needs the exec route below.
- Pick the status-bar Cmd textbox **by POSITION (`y > 900`)**, never by a `textbox` regex — the box can carry a `[focused]` tag, so the natural regex silently matches the Outliner search box instead and every exec command goes into the search field with no error. Symptom: commands appear to do nothing and no `Cmd:` line reaches the log.
- **`Click` the textbox once before the first `Type`** — an un-clicked box returns `returnValue:false` and swallows the command. Re-`Click` before each `Type`; typing steals focus.
- **`Type`'s "press enter" field is `submit`, not `pressEnter`.** A wrong field name is accepted, returns `true`, and types the text into the box WITHOUT executing it - so several commands silently accumulate and then run as one garbage line. Tell: taps appear to do nothing, then one `Cmd:` line shows every command concatenated. Keep one script with the correct shape and copy it rather than writing the call by hand.
- **Pause ~500ms between the `Click` and the `Type` too**, not only between taps: without it `Type` returns `Could not focus widget for typing` about half the time on a box it just clicked.
- **Pause ~500ms between consecutive tap execs.** Back-to-back taps each log as landed while the game advances only one step, so a drive silently loses a move and reads as a stuck menu.
- **A drive that stalls on a menu is usually a dropped keystroke, not a regression** — SlateInspector logs `Could not focus widget for typing` when a `Type` goes nowhere, while taps that land log their own line. Diff those before reading a stuck menu as a code fault; a stale PIE session restarted cleanly is the usual fix.
