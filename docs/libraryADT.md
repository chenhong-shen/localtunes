# library.py API

Version 2.0.0

The list of songs in the app. The library is saved in an SQLite database,
so it survives the app being closed. `Library` only records songs and keeps
that record in step with the `Music` folder. It does not download, play, or
show anything.

Replaces `download_history.py`.

## Identifiers

Each song has three ways of being identified, each with its own job:

| Identifier | Example | Used for |
|---|---|---|
| `id` | `4` | The song's number in the library. Chosen by the library when the song is added, and never reused, even after the song is deleted. Nothing else about the song is encoded in it. |
| `(platform, source_id)` | `('youtube', 'ZU4eX9a6f7M')` | Where the song came from. Used to tell whether a search result is already in the library, and to name thumbnails. |
| `filepath` | `'Song [ZU4eX9a6f7M].mp3'` | The song's file in the `Music` folder. Used by `sync` to match files to entries. Turned into a full path with `paths.song_path`. |

The valid platforms are:

| `platform` | `source_id` |
|---|---|
| `'youtube'` | The YouTube video ID, as described in the `search.py` API. |
| `'local'` | `None`. A local file has no source ID; its `filepath` identifies it. |

The library never holds two entries with the same `id`, the same
`filepath`, or the same `(platform, source_id)`. Any number of local songs
may coexist, because their `source_id` is `None`.

Only songs with a `source_id` can have a thumbnail.

## Entries

Each entry is a `dict` with exactly these keys:

| Key | Type | Meaning |
|---|---|---|
| `'id'` | `int` | The song's number, as described under [Identifiers](#identifiers). |
| `'platform'` | `str` | Where the song came from: `'youtube'` or `'local'`. |
| `'source_id'` | `str` or `None` | The song's ID on its platform, or `None` for local songs. |
| `'title'` | `str` | The song's title. Never empty. |
| `'artist'` | `str` | The song's artist. For YouTube downloads, the channel that uploaded the video. For songs found by `sync`, the file's `artist` tag, or `'Unknown'`. Never empty. |
| `'url'` | `str` | The song's page, for example `'https://www.youtube.com/watch?v=ZU4eX9a6f7M'`. Empty (`''`) for local songs. |
| `'filepath'` | `str` | The song's filename in the `Music` folder (not a full path). |
| `'downloaded_at'` | `str` | When the entry was recorded, in local time, in ISO format to the second, for example `'2026-10-08T22:35:00'`. For songs found by `sync`, this is when `sync` added them, not when the file was made. |

## Storage

Entries are stored in one table, `songs`, with one column per entry key:

| Column | Type and rules | Why |
|---|---|---|
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Filled in by SQLite. `AUTOINCREMENT` stops a deleted song's number from being given to a new song. |
| `platform` | `TEXT NOT NULL` | |
| `source_id` | `TEXT` | May be `NULL` (local songs). |
| `title`, `artist` | `TEXT NOT NULL` | A missing title or artist is rejected when saving, instead of breaking the pages that show it. |
| `url` | `TEXT NOT NULL DEFAULT ''` | |
| `filepath` | `TEXT NOT NULL UNIQUE` | One file is one song. |
| `downloaded_at` | `TEXT NOT NULL` | Set by Python, not SQLite, so every date has the same format and sorts correctly. |
| *(table rule)* | `UNIQUE (platform, source_id)` | The same video cannot be in the library twice. In SQLite, `NULL`s never clash, so local songs are not limited by this rule. |

Every change is saved (committed) before the public method that made it
returns, so a change is never lost if the app closes right afterwards. The
only exception is `add(..., autocommit=False)`, which `sync` uses
internally and commits itself.

The table is created only if it does not exist yet. A `library.db` from an
older version of the app, with different columns, is not upgraded: delete
it, and `sync` rebuilds the library from the `Music` folder.

## Threading

A `Library` must only be used on the thread that created it. This is a rule
of Python's `sqlite3` module: using it from another thread raises
`sqlite3.ProgrammingError`. In the app, the library is created and used
only on the main thread.

## class `Library`

Every song the app knows about.

---

### `Library(path)`

Constructor. Opens the library stored in a database file.

| | |
|---|---|
| `path` (`str`) | Path to the database file. The file does not need to exist yet, but its folder does. |
| **Returns** | `Library`. The library stored at `path`, or an empty library if no file exists there. |
| **Raises** | `sqlite3.DatabaseError` if the file exists but is not an SQLite database. `sqlite3.OperationalError` if the file cannot be opened or created. |

Creates the file immediately if it does not exist, and creates the `songs`
table if the file does not have one.

```python
library = Library(LIBRARY_FILE)
```

---

### `library.add(result, filepath, autocommit=True)`

Records a new song and, by default, saves it.

| | |
|---|---|
| `result` (`dict`) | The song's details, with at least the keys `'platform'`, `'source_id'`, `'title'`, `'artist'`, and `'url'`. A search result has exactly these keys. Not modified. |
| `filepath` (`str`) | The song's filename (not a full path). |
| `autocommit` (`bool`) | `True` (the default) to save the change immediately. `False` to leave it unsaved, so many songs can be saved together with one commit; the caller must then commit, or the change is lost when the app closes. Only `sync` passes `False`. |
| **Returns** | `int`. The new song's `id`. |
| **Raises** | `KeyError` if `result` is missing one of the required keys. `sqlite3.IntegrityError` if the library already has a song with this `filepath` or this `(platform, source_id)`, or if `title` or `artist` is `None`. `sqlite3.Error` if the database cannot be written. |

Never replaces an existing song: adding a song that is already in the
library raises `sqlite3.IntegrityError` and changes nothing.

```python
song_id = library.add(result, "Song [ZU4eX9a6f7M].mp3")
```

---

### `library.has(platform, source_id)`

Checks whether a song from a given source is in the library.

| | |
|---|---|
| `platform` (`str`) | A platform, for example `'youtube'`. |
| `source_id` (`str`) | The song's ID on that platform. |
| **Returns** | `bool`. `True` if the library has an entry with this `platform` and `source_id`. Always `False` when `source_id` is `None`. |

```python
library.has("youtube", "ZU4eX9a6f7M")
```

---

### `library.get_history(newest=True)`

Lists every entry, sorted by when it was recorded.

| | |
|---|---|
| `newest` (`bool`) | `True` (the default) for newest first, `False` for oldest first. |
| **Returns** | `list` of `dict`. Every entry, in the format described under [Entries](#entries). Empty if the library is empty. A fresh list, safe to modify. |

Entries recorded in the same second have no guaranteed order.

```python
library.get_history()             # newest first
library.get_history(newest=False) # oldest first
```

---

### `library.get_download_history(newest=True)`

Lists every entry where platform != 'local' in order to get the history of downloads, sorted by when it was downloaded.

| | |
|---|---|
| `newest` (`bool`) | `True` (the default) for newest first, `False` for oldest first. |
| **Returns** | `list` of `dict`. Every entry, in the format described under [Entries](#entries). Empty if the library is empty. A fresh list, safe to modify. |

Entries recorded in the same second have no guaranteed order.

```python
library.get_download_history()             # newest first
library.get_download_history(newest=False) # oldest first
```

---

### `library.get_metadata(filepath)`

Reads a song's title and artist from its file's tags, using mutagen. Only
reports what the tags say: choosing a fallback when a tag is missing is
left to the caller.

| | |
|---|---|
| `filepath` (`str`) | The FULL path of the song file. |
| **Returns** | `tuple` of `(title, artist)`. Each is a `str`, or `None` if the file has no such tag (or the tag is empty). Both are `None` if the file cannot be read at all. |
| **Raises** | Nothing. A missing, broken, or unrecognized file gives `(None, None)`, so one bad file cannot stop `sync`. |

If a tag holds several values (for example, several artists), only the
first is returned.

```python
library.get_metadata(song_path("my_song.mp3"))   # ('My Song', 'Some Artist')
library.get_metadata(song_path("no_tags.mp3"))   # (None, None)
```

---

### `library.sync(folder)`

Brings the library in step with the songs actually in `folder`, and saves
the result. Called when the app starts, by the All Songs page's Rescan
button, and by `App.resync` when a song's file is found to be missing.

| | |
|---|---|
| `folder` (`str`) | The music folder, normally `MUSIC_FOLDER`. Created if it does not exist. |
| **Returns** | `None`. |
| **Raises** | `OSError` if `folder` cannot be created or read. `sqlite3.Error` if the database cannot be written. |

A song is any file directly in `folder` whose name ends in `.mp3`, in any
capitalization. Subfolders and other files are ignored.

After `sync`, the library holds one entry for each song in `folder`, and no
others:

- **In the library, but its file is gone:** the entry is removed. Its
  thumbnail, if any, is left in place.
- **In `folder`, but not in the library:** an entry is added with
  `add`, built as follows.

| Key | Value |
|---|---|
| `'platform'` | `'youtube'` if the filename (without `.mp3`) ends in `[<11-character id>]`, otherwise `'local'`. |
| `'source_id'` | That YouTube ID, or `None` for local files. |
| `'title'` | The file's `title` tag, from `get_metadata`. If it has none, the filename without `.mp3` and without the ` [<id>]` part. |
| `'artist'` | The file's `artist` tag, from `get_metadata`, or `'Unknown'` if it has none. |
| `'url'` | `'https://www.youtube.com/watch?v=<id>'` for YouTube files, otherwise `''`. |

For example, a file with no tags named
`Nightcore - Solo Tu Remix (Quality Remake) [ZU4eX9a6f7M].mp3` is added as:

```python
{
    "platform": "youtube",
    "source_id": "ZU4eX9a6f7M",
    "title": "Nightcore - Solo Tu Remix (Quality Remake)",
    "artist": "Unknown",
    "url": "https://www.youtube.com/watch?v=ZU4eX9a6f7M",
}
```

**Duplicates:** if two files in `folder` hold the same YouTube video (the
same `[<id>]` under different names), only one is added; the other is
skipped. Which one is kept is not defined. The skipped file is found again,
and skipped again, by every later `sync`.

Entries whose file is still in `folder` are not changed. Calling `sync`
twice in a row changes nothing the second time. If nothing was added or
removed, nothing is written to the database.

A file that was renamed is treated as one song removed and one song added,
so it gets a new `id`. Because thumbnails are named after the song's source
and not its `id`, a renamed YouTube song keeps its thumbnail.

A file that cannot be read is still added, using its filename as the title.

Every removal and addition is saved together, with one commit at the end.
This makes a large sync fast (about 0.6 s for 2,000 new files), and makes
it all-or-nothing: if `sync` fails partway, none of its changes are saved.
