# paths.py API

Version 2.0.0

Where LocalTunes keeps its files. App data is stored under `APP_DIR`, whether
the program is run from source or as a PyInstaller build. `paths.py` only
works out paths. It does not create, read, or check any file.

## Module constants

### `APP_DIR`

`str`. The folder the app lives in: the folder holding `main.py` when run
from source, or the folder holding the `.exe` when run as a PyInstaller
build.

### `MUSIC_FOLDER`

`str`. `APP_DIR` joined with `"Music"`. The folder songs are saved to and
synced with the library. Passed to `MusicService`, which passes it to
`Download` and `Library.sync`.

### `THUMBNAIL_FOLDER`

`str`. `APP_DIR` joined with `"thumbnails"`. The folder song thumbnails are
saved to. Each thumbnail is named `<platform>_<source_id>.jpg`, for example
`youtube_ZU4eX9a6f7M.jpg`.

### `LIBRARY_FILE`

`str`. `APP_DIR` joined with `"library.db"`. The library database. Passed
to `Library`.

### `FFMPEG_FOLDER`

`str`. `APP_DIR` joined with `"bin"`. The folder holding `ffmpeg.exe` and
`ffprobe.exe`. Passed to `MusicService` and then to `Download`.

### `ENV_FILE`

`str`. `APP_DIR` joined with `".env"`. `search.py` loads this file to make
`YT_API_KEY` available to YouTube searches. The path module does not create
the file.

## Module functions

### `song_path(filename)`

Gives the full path of a song.

| | |
|---|---|
| `filename` (`str`) | A song's filename, as stored in a library entry's `'filepath'` field. |
| **Returns** | `str`. `MUSIC_FOLDER` joined with `filename`. The file may or may not exist; callers should check before using it. |

The library stores only filenames, not full paths, so it stays valid if the
app folder is moved. Use this to turn one back into a real path.

---

### `thumbnail_path(platform, source_id)`

Gives the path a song's thumbnail is (or would be) saved at.

| | |
|---|---|
| `platform` (`str`) | The song's platform, for example `'youtube'`. |
| `source_id` (`str`) | The song's ID on that platform. Should not be `None`: every song without one would share the path `local_None.jpg`. `load_thumbnail` checks for this before calling. |
| **Returns** | `str`. `THUMBNAIL_FOLDER` joined with `<platform>_<source_id>.jpg`. The file may or may not exist. |

Thumbnails are named after the song's source, not its library `id`, so a
song that is removed and added again finds its picture again.
