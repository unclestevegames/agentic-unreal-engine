# Routing input in general

How a press, a typed character or a held button reaches the game, in any screen.

- **Only a live seam can catch a half-wired input**: a spec that calls the widget's own command handler never sees a missing `IE_Released` binding, and the press-only direction then arms a repeat nothing can stop. Walk `UInputComponent`'s own action bindings instead.
- **Real typed characters reach the game ONLY through `UGameViewportClient::InputChar`.** A Slate input pre-processor cannot do it - `IInputProcessor` declares no character handler at all - and `FKeyEvent::GetCharacter()` carries `MapVirtualKey(.., MAPVK_VK_TO_CHAR)`, the key's UNSHIFTED character, uppercase for every letter, so a field built on it types in capitals and turns Shift+3 into `3`.
- **`FInputModeGameOnly` already focuses the game viewport**, which is what delivers `OnKeyChar` there - so reading a keyboard needs no input-mode change, and a field that never changes the mode has no mode to hand back and no exit path to miss.
- **A viewport client that takes typing must let the dev console have it first** (`ViewportConsole->ConsoleActive()`). Without that, console commands are typed into the field and the terminating Enter saves the command line as the value.
- **A button still held when the level changes arrives on the next screen as a real press.** UE synthesises an `IE_Pressed` when the new `UPlayerInput` (empty key-state map) sees a repeat for a key it never saw pressed, and that fires the press bindings. Refuse `IE_Repeat` in the player controller's `InputKey`; anything that starts binding repeats reopens it.
- **`IOnlineExternalUI` has NO `ShowVirtualKeyboard` in UE 5.8**, and nothing in the engine wraps Steam's
  on-screen keyboard. It is reachable only as `ISteamUtils::ShowGamepadTextInput` + the
  `GamepadTextInputDismissed_t` callback.
- **`ShowGamepadTextInput` answers false unless Steam's overlay is up in Big Picture or on a Deck.**
  Decide which entry path a machine takes from that RETURN, never from asking what kind of machine it is.
