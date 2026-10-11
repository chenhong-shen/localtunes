# play_queue.py API

Version 1.0.0

`PlayQueue` keeps a playback order for a snapshot of library song entries. It
does not read the library, play audio, or change song metadata. Songs are
matched by their `'filepath'` value.

## class `PlayQueue`

### `PlayQueue(song_list, shuffle_enabled=False)`

Creates a queue from a shallow copy of `song_list`. When shuffle is off, the
initial order is unchanged; when shuffle is on, it is randomized. No current
song is selected, so `song_index` starts at `-1`.

| Argument | Meaning |
|---|---|
| `song_list` (`list` of song `dict`s) | Source songs. Each song should have a `'filepath'` key. The list itself is copied. |
| `shuffle_enabled` (`bool`) | Whether to begin in shuffled mode. Defaults to `False`. |
| **Returns** | `PlayQueue`. |

#### State

| Attribute | Meaning |
|---|---|
| `song_list` | A shallow copy of the source list. Queue operations do not reorder it, except `set_current` appends a song that was not present when shuffle is off. Song dictionaries are shared references. |
| `queue` | Current playback order. `create_queue` returns this same mutable list, containing the same song-dictionary references. |
| `song_index` | Index of the current song, or `-1` when no current song is set. |
| `shuffle_enabled` | Whether a new order is randomized and the queue cycles in shuffled rounds. |

### `queue.create_queue(current_song=None)`

Rebuilds the playback order from `song_list` and returns the internal `queue`
list. Songs are matched by `'filepath'`.

When shuffle is enabled and a current song is found, that song is placed at
index 0 and the remaining songs are shuffled. Otherwise, all songs are
shuffled and the index is `-1`. With shuffle off, source order is restored
and the index points to the current song if found. If `current_song` is
omitted or `None`, the existing `current_song()` value is used when one is
available.

### `queue.set_songs(song_list)`

Replaces the source snapshot and rebuilds the order, retaining the active
song by filepath when it remains in the new list. Returns `None`.

### `queue.set_current(song)`

Sets `song` as the active entry. If its filepath is present in the source
list, shuffle mode puts it at index 0 and shuffles the remaining songs; with
shuffle off, its index is set in source order. If the filepath is absent,
shuffle mode leaves the index at `-1`; with shuffle off, the song is appended
to `song_list` and the queue is rebuilt. Returns `None`.

### `queue.toggle_shuffle(current_song=None)`

Flips `shuffle_enabled`, rebuilds the queue, and keeps the supplied current
song in place when possible. Returns the new `bool` state.

### `queue.next_song()`

Advances and returns the next song entry. If no current song was set, returns
the first song. At the end of an unshuffled queue, wraps to the first song.
At the end of a shuffled queue, starts another randomized round while keeping
the just-played song first and selecting the following item; this avoids an
immediate repeat when the queue has more than one song. A one-song shuffled
queue returns that song again. Returns `None` when the queue is empty.

### `queue.current_song()`

Returns the song entry at `song_index`, or `None` if the index does not point
to an entry.
