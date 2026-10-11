# player.py API

Version 1.0.0

## class `Player`

`Player` is the audio player for `.mp3` files. It only plays one track at a
time: it does not handle playlists, the UI, or connecting these together.

---

### `Player()`

Constructor. Creates a player with nothing loaded, and initializes pygame's
music player (`pygame.mixer.init()`), which does the actual playback.

| | |
|---|---|
| **Returns** | `Player`. A player with nothing loaded. |

#### State

Every attribute is set when the player is created, so none of them can be
read before it exists.

| Attribute | Type | Starts as | Meaning |
|---|---|---|---|
| `length` | `float` | `0` | The loaded track's length, in seconds. |
| `offset` | `float` | `0` | Where in the track playback last started from, in seconds. See below. |
| `loaded` | `bool` | `False` | Whether a track is loaded. |
| `started` | `bool` | `False` | Whether the loaded track has started playing. |
| `paused` | `bool` | `False` | Whether playback is paused. |
| `stopped` | `bool` | `False` | Whether playback was stopped on purpose. |

#### Why `offset` exists

pygame's `get_pos()` doesn't report where playback is in the track. It reports
how long the track has been playing **since `play()` was last called**, so it
restarts at 0 every time playback starts, no matter where in the track that is.

Seeking works by restarting playback at a new point, so without a correction
the position would jump back to 0 after every seek. `offset` records where
playback started, and the position is calculated as:

```
position = offset + get_pos() / 1000
```

`get_pos()` is in milliseconds, hence the `/ 1000`.

---

### `Player.load(filepath)`

Loads a song from a filepath. Think of loading as putting a round in the
chamber: it doesn't play or start the song, just loads it so it's ready to be
used. Loading a new song replaces the one that was loaded before.

| | |
|---|---|
| `filepath` (`str`) | The FULL path of the mp3 file to play. Proper formatting should be handled at INPUT, as it is not handled here. |
| **Returns** | `None`. |
| **Raises** | `TypeError` if `filepath` is not a `str`. `FileNotFoundError` if the file could not be found. Errors from mutagen or pygame if the file exists but isn't a readable mp3. |

| Attribute | Type | New Value | Meaning |
|---|---|---|---|
| `length` | `float` | `MP3(filepath).info.length` | The loaded track's length, in seconds. |
| `offset` | `float` | `0` | Loading a new track sets the offset to 0, since no seeking has been done yet. |
| `loaded` | `bool` | `True` | The track has now been loaded. |
| `started` | `bool` | `False` | Loading does not start playing the track automatically. |
| `paused` | `bool` | `False` | A newly loaded track is not paused. |
| `stopped` | `bool` | `False` | A newly loaded track is not stopped. |

---

### `Player.play()`

Plays the loaded song from the beginning. If the song is already playing,
paused, stopped, or finished, it starts over.

| | |
|---|---|
| **Returns** | `None`. |
| **Raises** | `RuntimeError` if no song is currently loaded. |

| Attribute | Type | New Value | Meaning |
|---|---|---|---|
| `offset` | `float` | `0` | Playback starts from the beginning, so the offset resets to 0. |
| `started` | `bool` | `True` | The song has now been started, and is playing. |
| `paused` | `bool` | `False` | Playing un-pauses the song. |
| `stopped` | `bool` | `False` | Playing clears a previous stop. |

---

### `Player.pause()`

Pauses the currently playing song. Playback can be continued from the same
spot with `resume()`.

| | |
|---|---|
| **Returns** | `None`. |
| **Raises** | Nothing. If no song is playing, playback is unaffected. |

| Attribute | Type | New Value | Meaning |
|---|---|---|---|
| `paused` | `bool` | `True` | Pausing pauses the track. |

---

### `Player.resume()`

Continues a paused song from where it was paused. Unlike `play()`, it does not
start over.

| | |
|---|---|
| **Returns** | `None`. |
| **Raises** | Nothing. If no song is paused, playback is unaffected. |

| Attribute | Type | New Value | Meaning |
|---|---|---|---|
| `paused` | `bool` | `False` | Resuming unpauses the track. |

---

### `Player.stop()`

Stops the currently loaded song. The song stays loaded, so `play()` starts
it again from the beginning. A stopped song does not count as finished.

| | |
|---|---|
| **Returns** | `None`. |
| **Raises** | Nothing. If no song is playing, playback is unaffected. |

| Attribute | Type | New Value | Meaning |
|---|---|---|---|
| `paused` | `bool` | `False` | Stopping the song resets pause to false. |
| `stopped` | `bool` | `True` | Stopping the song sets stopped to True. |

---

### `Player.seek(seconds)`

Jumps to a point in the loaded song. Seeking works by restarting playback at
that point, so it also starts a song that was stopped, finished, or never
started. If the song was paused, it stays paused at the new point.

| | |
|---|---|
| `seconds` (`int` or `float`) | Where to jump to, in seconds from the start. Values below 0 are treated as 0, and values past the end are treated as the end. |
| **Returns** | `None`. |
| **Raises** | `RuntimeError` if no song is currently loaded. |

| Attribute | Type | New Value | Meaning |
|---|---|---|---|
| `offset` | `float` | `seconds`, kept between `0` and `length` | Playback now starts from this point, so `position()` counts from here. |
| `started` | `bool` | `True` | Seeking starts playback. |
| `stopped` | `bool` | `False` | Seeking clears a previous stop. |
| `paused` | `bool` | Unchanged | A paused song stays paused; a playing song keeps playing. |

---

### `Player.position()`

Gives how far into the song playback is.

| | |
|---|---|
| **Returns** | `float`. The position in seconds, between `0` and `duration()`. `0` if nothing has started playing, or if the song was stopped. |
| **Raises** | Nothing. |

Does not change any attributes. See [Why `offset` exists](#why-offset-exists)
for how the position is calculated.

---

### `Player.duration()`

Gives the length of the loaded song.

| | |
|---|---|
| **Returns** | `float`. The length in seconds. `0` if nothing is loaded. |
| **Raises** | Nothing. |

Does not change any attributes. The length is read once, when the song is
loaded, so calling this is instant.

---

### `Player.is_playing()`

Checks whether the song is audibly playing right now.

| | |
|---|---|
| **Returns** | `bool`. `True` if a song has been started and is not paused, stopped, or finished. |
| **Raises** | Nothing. |

Does not change any attributes.

---

### `Player.is_finished()`

Checks whether the song reached its end on its own. Used to know when to move
on to the next song.

| | |
|---|---|
| **Returns** | `bool`. `True` if a song was started, is not paused or stopped, and has stopped making sound. `False` if nothing has started, or if the song was paused or stopped on purpose. |
| **Raises** | Nothing. |

Does not change any attributes. A finished song can be played again with
`play()` or `seek()`.

#### Playback states

At any moment, the player is in exactly one of these states:

| State | `is_playing()` | `is_finished()` | How you get there |
|---|---|---|---|
| Nothing loaded | `False` | `False` | A new `Player()`. |
| Loaded, not started | `False` | `False` | `load()`. |
| Playing | `True` | `False` | `play()`, `resume()`, or `seek()` while playing. |
| Paused | `False` | `False` | `pause()`, or `seek()` while paused. |
| Stopped | `False` | `False` | `stop()`. |
| Finished | `False` | `True` | The song plays to its end. |