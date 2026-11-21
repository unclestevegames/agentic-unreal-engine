# Fixtures that answer to the machine

Every way a spec ends up answering to the box it runs on rather than to the game: files the player
writes (settings, saves, reports) and the platform layer. A spec touching any of them redirects or pins
it for the whole file.

- **A spec whose subject asks the platform layer needs that layer PINNED**, or it silently answers to whether the box running it happens to have Steam up. Pin it for the whole file (some leaves pinned and some not is the same coupling one level down), and write one leaf pinning it the other way - a pin never observed to change behaviour is decoration.
- **The first setting that changes GAMEPLAY couples every spec exercising it to the machine's own settings file** - not the same file on two developers' boxes, and a shipped default then decides what a press does. Any fixture pressing a button whose behaviour a setting governs needs a guard that redirects it.
  - …but only where the press can actually reach the store: a guard on a press that never asks hides the regression that makes it ask.
  - **A setting read at widget CONSTRUCTION couples every leaf in the file, not just the ones about it.** Redirect in `BeforeEach` BEFORE the widget exists and restore in `AfterEach`.
- **A reset that clears a CACHE leaves the FILE** - a leaf that changes a choice leaves it on disk at the redirected path for the next leaf's fresh load to read back. Delete the file yourself in `BeforeEach` and `AfterEach`.
- **A row that decides where the highlight OPENS must have its store redirected in the fixture.** A row whose availability comes off a file lands the cursor wherever the box's own disk says.
- **A payload that embeds the machine's real settings file** answers to whatever a live drive last saved, in any assertion over its text. Redirect settings to a spec-owned file in `BeforeEach`.
- **A blind press onto a "default highlight" answers to whatever the box left behind** - a row enabled only while a save sits on disk moves every row under it - so a blind walk reaches a different row depending on which spec ran first. Walk to the row BY NAME.
