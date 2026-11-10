# music_service.py API

Version 1.1.0

`MusicService` coordinates app workflows between the UI and the lower-level
library, YouTube search, downloader, and thumbnail modules. Pages use this
service instead of importing those modules or calling `Library` directly.

## Threading

The SQLite `Library` connection is created by the app and must only be used
on that same thread. Therefore `sync_library`, the library read methods, and
`record_download` run on the main thread. `search`, `get_url_metadata`, and
`download` perform network or file work without touching SQLite and may run
on worker threads. Worker threads must still report results to the UI through
its event queue; they must never update widgets.

## class `MusicService`

### `MusicService(library, music_folder, ffmpeg_folder)`

Creates the app's service facade. It does not open or sync the database.

#### State

| Attribute | Meaning |
|---|---|
| `library` | The injected `Library` instance. |
| `music_folder` | Audio folder used by sync and downloads. |
| `ffmpeg_folder` | ffmpeg tools folder passed to the downloader. |

| Argument | Meaning |
|---|---|
| `library` (`Library`) | The app's SQLite library instance. |
| `music_folder` (`str`) | Destination and sync folder for audio files. |
| `ffmpeg_folder` (`str`) | Folder containing ffmpeg tools used by the downloader. |
| **Returns** | `MusicService`. |

### `service.sync_library()`

Calls `Library.sync(music_folder)` to reconcile database rows with audio files
on disk. **Main thread.** Returns `None`. Propagates filesystem or SQLite
errors from `Library.sync`.

### `service.get_all_songs()`

Returns all library entries by delegating to `Library.get_all_songs()`.
The order is unspecified. **Main thread.**

| | |
|---|---|
| **Returns** | `list` of song-entry `dict`s. |

### `service.get_history(newest=True)`

Returns the song history in the order requested by `newest`, delegating to
`Library.get_history`. **Main thread.**

| | |
|---|---|
| `newest` (`bool`) | `True` for newest first; `False` for oldest first. |
| **Returns** | `list` of song-entry `dict`s. |

### `service.get_download_history(newest=True)`

Returns downloaded (non-local) entries in the order requested by `newest`,
delegating to `Library.get_download_history`. **Main thread.**

| | |
|---|---|
| `newest` (`bool`) | `True` for newest first; `False` for oldest first. |
| **Returns** | `list` of non-local song-entry `dict`s. |

### `service.has_song(platform, source_id)`

Returns whether the library contains the given platform/source pair.
Delegates to `Library.has`; `source_id=None` returns `False`. **Main thread.**

| | |
|---|---|
| `platform` (`str`) | Platform to look up. |
| `source_id` (`str` or `None`) | Source ID to look up. |
| **Returns** | `bool`. |

### `service.search(query, platform="YouTube", max_results=10)`

Searches the selected catalog and returns result dictionaries in the
`Search.search_youtube` format. Currently only `"YouTube"` is supported;
other platform names raise `ValueError`. May run on a worker thread. Search
validation and network errors from `Search` are propagated to the caller.

| | |
|---|---|
| `query` (`str`) | Search text. |
| `platform` (`str`) | Currently only `"YouTube"` is accepted. |
| `max_results` (`int`) | Number of results to request; `Search` accepts 1 through 50. |
| **Returns** | `list` of search-result `dict`s. |
| **Raises** | `ValueError` for an unsupported platform; otherwise errors from `Search` propagate. |

### `service.get_url_metadata(url, platform)`

Extracts metadata for a YouTube URL without downloading its audio. Uses
`yt_dlp` and returns a result dictionary compatible with `service.download`
and `Library.add`. May run on a worker thread; does not access SQLite.

| | |
|---|---|
| `url` (`str`) | YouTube video URL to inspect. |
| `platform` (`str`) | Platform identifier to store in the result, normally `"youtube"`. |
| **Returns** | `dict` with `platform`, `source_id`, `title`, `artist`, and `url`. |
| **Raises** | An exception if yt-dlp cannot extract the metadata or required metadata fields are unavailable. |

The `artist` value is taken from yt-dlp's `artist` field, falling back to its
`channel` field. The `url` in the result is the supplied URL.

### `service.download(result)`

Downloads the result audio into `music_folder`, attempts to save its
thumbnail, and returns the full audio filepath. Thumbnail errors are ignored
because artwork is optional. May run on a worker thread. Downloader errors
are propagated to the caller. Does not access SQLite.

### `service.record_download(result, filepath)`

Records a completed download with `Library.add`, storing only the basename of
`filepath`, and returns the inserted SQLite row ID. **Main thread only**
because the library connection belongs to the app thread. SQLite errors are
propagated to the caller.

### Playlist methods

Thin wrappers over the `Library` playlist methods of the same names; see
the Playlists section of the `library.py` API for what each one returns.
They all use SQLite, so they are **main thread only**.

| Method | Calls |
|---|---|
| `service.get_playlists()` | `Library.get_playlists()` |
| `service.create_playlist(name)` | `Library.create_playlist(name)` |
| `service.rename_playlist(pid, name)` | `Library.rename_playlist(pid, name)` |
| `service.delete_playlist(pid)` | `Library.delete_playlist(pid)` |
| `service.get_playlist_songs(pid)` | `Library.get_playlist_songs(pid)` |
| `service.add_to_playlist(pid, song_id)` | `Library.add_to_playlist(pid, song_id)` |
| `service.remove_from_playlist(pid, song_id)` | `Library.remove_from_playlist(pid, song_id)` |
