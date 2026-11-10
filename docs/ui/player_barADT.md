# ui/player_bar.py API

Version 2.0.0

The playback bar along the bottom of the window. `PlayerBar` shows what is
playing and controls the app's `Player`. It does not choose what to play:
it plays whatever song it is given, and picks the next song from either
the whole library or the playlist being played. It reads the available
songs through `MusicService`. It does not change the library: when a song's
file is missing, it calls the `on_missing` function it was given.

## class `PlayerBar`

Subclass of `customtkinter.CTkFrame`.

Layout, left to right:

```
[ art ] [ title / artist / source ]  ( ▶ )  [ ========o-------- ]  0:00 / 0:00
```

The bar keeps itself up to date by checking the player every 500 ms, in
`refresh()`. Every method runs on the **main thread**.

#### State

| Attribute | Type | Starts as | Meaning |
|---|---|---|---|
| `player` | `Player` | The given player | The player the bar controls. |
| `service` | `MusicService` | The given service | Reads the available songs for queue setup and refresh. |
| `on_missing` | function | The given function | Called when a song passed to `play_song` has a missing file. |
| `shuffle_enabled` | `bool` | `False` | Whether automatic next-track playback uses the shuffled queue. |
| `PlayQueue` | `PlayQueue` | Queue made from the service's current songs | Tracks song order and current song. |
| `queue_source` | `int` or `None` | `None` | Where the next song comes from: `None` for the whole library, or the `id` of the playlist being played. Set by `play_from_library` and `play_playlist`. |
| `user_seeking` | `bool` | `False` | `True` while the mouse button is held down on the progress slider. While it is `True`, `refresh()` does not move the slider or change the time, so they don't jump while being dragged. |

---

### `PlayerBar(parent, player, on_missing, service)`

Constructor. Builds the bar, showing "Nothing playing", and starts
`refresh()`.

| | |
|---|---|
| `parent` | The widget the bar belongs in. |
| `player` (`Player`) | The app's player. |
| `on_missing` (function) | Called as `on_missing()`, with no arguments, when `play_song` finds that the song's file is gone, whether selected in the library or reached by shuffle. In the app, this is `App.resync`. |
| `service` (`MusicService`) | Provides the current library song list for queue setup and refresh. |
| **Returns** | `PlayerBar`. |

---

### `bar.play_from_library(song)`

Sets `queue_source` to `None` and plays `song` with `play_song`, so the
next songs come from the whole library. Given to `LibraryPage` as its
`on_play` function.

---

### `bar.play_playlist(playlist_id, start=None)`

Sets `queue_source` to `playlist_id` and plays `start` (a song in the
playlist), or the first song in queue order if `start` is `None`. With
shuffle on, that first song is random. Does nothing if the playlist is
empty. Given to `PlaylistsPage` as its `on_play_playlist` function.

---

### `bar.show_queue_source()`

Sets the small gray line under the artist to "Playing from All Songs" or
"Playing from <playlist name>" (names over 24 characters are cut with "…"),
from `queue_source`. The playlist's name is looked up each time, so a rename
shows; a playlist that no longer exists shows as "a deleted playlist". Does
nothing until a song has been played. Called by `play_from_library` and
`play_playlist`, and given to `PlaylistsPage` as its `on_playlists_changed`
function so renames and deletes show right away.

---

### `bar.play_song(song)`

Loads and plays a song, and shows its details. Used by `play_from_library`,
`play_playlist`, and `refresh` (for the next song). Does not change
`queue_source`.

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

Any previously loaded song stays loaded but stopped; if none was loaded, the
player remains unloaded. The play button and slider do nothing until another
song is played (see `toggle_play_pause` and `on_seek_release`).

After successful playback, the song is made current in `PlayQueue`. When
shuffle is enabled, the selected song becomes the start of a newly shuffled
remainder.

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
alone. When the song finishes, the next song is played automatically, from the
songs `queue_source` points to (re-read each time, so changes made while
playing count). With shuffle off, songs play in order and the last one wraps
around to the first. If there is nothing to play, the button changes back
to ▶.

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

---

### `bar.toggle_shuffle()`

Toggles shuffle and updates the button's visual state. **Main thread.** When
shuffle is enabled, the current song is placed first and the remaining songs
are randomized. When disabled, source order is restored and the current
song's index is retained. Returns `None`.
