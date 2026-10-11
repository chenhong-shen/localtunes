# ui/player_bar.py API

Version 1.2.0

The playback bar along the bottom of the window. `PlayerBar` shows what is
playing and controls the app's `Player`. It does not choose what to play:
it plays whatever song it is given in `play_song`. It does not change the
library either: when a song's file is missing, it calls the `on_missing`
function it was given.

## class `PlayerBar`

Subclass of `customtkinter.CTkFrame`.

Layout, left to right:

```
[ art ] [ title / artist ]  ( ▶ )  [ ========o-------- ]  0:00 / 0:00
```

The bar keeps itself up to date by checking the player every 500 ms, in
`refresh()`. Every method runs on the **main thread**.

#### State

| Attribute | Type | Starts as | Meaning |
|---|---|---|---|
| `player` | `Player` | The given player | The player the bar controls. |
| `on_missing` | function | The given function | Called when a clicked song's file is missing. |
| `user_seeking` | `bool` | `False` | `True` while the mouse button is held down on the progress slider. While it is `True`, `refresh()` does not move the slider or change the time, so they don't jump while being dragged. |

---

### `PlayerBar(parent, player, on_missing)`

Constructor. Builds the bar, showing "Nothing playing", and starts
`refresh()`.

| | |
|---|---|
| `parent` | The widget the bar belongs in. |
| `player` (`Player`) | The app's player. |
| `on_missing` (function) | Called as `on_missing()`, with no arguments, when `play_song` finds that the song's file is gone. In the app, this is `App.resync`. |
| **Returns** | `PlayerBar`. |

---

### `bar.play_song(song)`

Loads and plays a song, and shows its details. Given to `LibraryPage` as its
`on_play` function, so it is called when a song box is clicked.

| | |
|---|---|
| `song` (`dict`) | A library entry, with at least the keys `'platform'`, `'source_id'`, `'title'`, `'artist'`, and `'filepath'`. |
| **Returns** | `None`. |
| **Raises** | Any error raised by `Player.load` if the file exists but is not a readable mp3. A missing file does not raise. |

Shows the title (shortened with "…" past 30 characters), the artist
(shortened with "…" past 15 characters), and the thumbnail at 64x36, or a ♪
placeholder if there is none (always the case for local songs). The play button changes to ⏸.

**If the song's file is missing**, nothing is loaded. Instead:

1. Playback of the current song is stopped.
2. The bar shows "File not found", with the missing song's title
   (shortened past 30 characters) on the second line, the ♪ placeholder,
   and ▶ on the play button.
3. `on_missing()` is called, so the app can resync and remove the song.

The previous song stays loaded in the player but stopped, and the play
button and slider do nothing until another song is played (see
`toggle_play_pause` and `on_seek_release`).

When this is called from a click on a song box, nothing catches errors
from `Player.load`: a broken file is reported in the console, and nothing
visible happens in the app.

---

### `bar.toggle_play_pause()`

Pauses, resumes, or replays the loaded song. Called when the play button is
clicked.

| | |
|---|---|
| **Returns** | `None`. |

| Player state | Effect | Button shows |
|---|---|---|
| Nothing loaded | Nothing. | Unchanged |
| Stopped (after a missing file) | Nothing. The loaded song is the previous one, so playing it would not match what the bar shows. | Unchanged (▶) |
| Finished | Plays the song again from the start. | ⏸ |
| Playing | Pauses. | ▶ |
| Anything else | Resumes. | ⏸ |

---

### `bar.refresh()`

Updates the time and the progress slider from the player, then schedules
itself to run again in 500 ms. Started once, by the constructor, and runs
for the life of the bar.

| | |
|---|---|
| **Returns** | `None`. |

The time is shown as `"<position> / <length>"`, formatted with
`format_time`. While `user_seeking` is `True`, the time and slider are left
alone. When the song finishes, the play button changes back to ▶.

---

### `bar.on_seek_drag(value)`

Shows the time the slider points at while it is being dragged, without
seeking yet. Called by the slider as it moves.

| | |
|---|---|
| `value` (`float`) | The slider's position, from `0` (start of the song) to `1` (end). |
| **Returns** | `None`. |

---

### `bar.on_seek_release()`

Seeks to where the slider was released, and lets `refresh()` move the
slider again. Called when the mouse button is released on the slider.

| | |
|---|---|
| **Returns** | `None`. |

Does nothing but clear `user_seeking` if no song is loaded, or if playback
is stopped after a missing file (seeking would restart the previous song).
A paused song stays paused at the new point; otherwise the play button
shows ⏸.
