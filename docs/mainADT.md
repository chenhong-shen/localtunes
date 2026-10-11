# main.py API

Version 2.3.0

The LocalTunes main window. `App` builds the window and connects the pieces:
the pages, the player bar, the music service, and the player. `App` wires
these pieces together; workflows that coordinate search, downloads, and the
library live in `MusicService`. Each piece lives in its own file:

| File | Holds | Documented in |
|---|---|---|
| `ui/library_page.py` | `LibraryPage`: the All Songs grid | `ui/library_pageADT.md` |
| `ui/search_page.py` | `SearchPage`: searching and downloading | `ui/search_pageADT.md` |
| `ui/downloads_page.py` | `DownloadsPage`: the download list | `ui/downloads_pageADT.md` |
| `ui/player_bar.py` | `PlayerBar`: the playback bar | `ui/player_barADT.md` |
| `ui/page.py` | `Page`: the base class of every page | `ui/pageADT.md` |
| `ui/plain.py` | Plain Tk labels and card helpers | `ui/plainADT.md` |
| `ui/formatting.py` | Re-exports the formatting helpers | `formattingADT.md` |
| `music_service.py` | `MusicService`: coordinates app workflows | `music_serviceADT.md` |
| `play_queue.py` | `PlayQueue`: tracks playback order and shuffle | `play_queueADT.md` |
| `search.py` | `Search`: finds videos on YouTube | `searchADT.md` |
| `downloader.py` | `Download`: downloads a video's audio | `downloaderADT.md` |
| `library.py` | `Library`: the database of songs | `libraryADT.md` |
| `player.py` | `Player`: plays one song | `playerADT.md` |
| `paths.py` | Where every file is kept | `pathsADT.md` |
| `thumbnails.py` | Saving and loading song pictures | `thumbnailsADT.md` |
| `formatting.py` | Turning times and dates into text | `formattingADT.md` |

## Running the app

```python
python main.py
```

When `main.py` is run, it creates one `App` and starts its main loop. The
`App` syncs the library with the `Music` folder as it starts, so songs
added or deleted while the app was closed are picked up.

## Identifiers

Pages are identified by the page object itself. Each page has a display
label, shown on its sidebar button and as the page title: `"All Songs"`,
`"Playlists"`, `"Search"`, `"Downloads"`, and `"Settings"`. Labels and pages
are paired once, in a single list, so every sidebar button has exactly one
matching page.

## class `App`

The main window. Subclass of `customtkinter.CTk`.

Layout:

```
| sidebar | the current page          |   row 0 (stretches)
|          player bar                 |   row 1
```

The sidebar on the left has one button per page. All pages occupy the same
place in the window, and exactly one is shown at a time. The player bar
runs along the bottom, under both.

Playlists and Settings have no content yet: they are plain `Page`s showing
only their title.

Each page is given only what it needs, and never reaches into the `App`.
Pages receive the `MusicService` for library, search, download, and sync
operations. They use callbacks only for UI actions such as refreshing views,
playing a selected song, or responding to a missing file.

#### State

| Attribute | Type | Meaning |
|---|---|---|
| `library` | `Library` | The SQLite library used by the service. |
| `service` | `MusicService` | Coordinates data and download workflows for the UI. |
| `player` | `Player` | The app's one player, used by the player bar. |
| `player_bar` | `PlayerBar` | The playback bar, which owns the current play queue. |
| `library_page` | `LibraryPage` | The All Songs page. |
| `search_page` | `SearchPage` | The Search page. |
| `downloads_page` | `DownloadsPage` | The Downloads page. |

---

### `App()`

Constructor. Opens the library at `LIBRARY_FILE`, creates a `MusicService`,
and asks it to sync with `MUSIC_FOLDER`. Then it creates the player and builds the window, the player bar,
every page, and the sidebar. **Main thread.**

| | |
|---|---|
| **Returns** | `App`. A window showing the All Songs page. The window is not displayed until `mainloop()` is called. |
| **Raises** | Any error raised by `Library` while opening or syncing the library, for example if `LIBRARY_FILE` exists but is not an SQLite database, or `MUSIC_FOLDER` cannot be read. |

The service owns the workflow boundary. The SQLite library remains on the
main thread; the service uses it for startup sync and later UI reads/writes.

The player bar is built before the pages, because the All Songs page needs
its `play_song` method. The player bar is given `resync` as its
`on_missing` function, and the All Songs page is given it as `on_rescan`
(the button is labeled "Refresh").
This is safe even though `resync` uses pages built later (the Downloads
page), because it is only called later, after every page exists.

```python
App().mainloop()
```

---

### `app.show(page)`

Shows one page and hides the others. **Main thread.**

| | |
|---|---|
| `page` (`Page`) | One of the app's pages. |
| **Returns** | `None`. |

---

### `app.refresh_library_views()`

Redraws the All Songs and Downloads pages after `MusicService` records a
download. Called by `SearchPage` on the main thread. It does not read or
write the library.

---

### `app.resync()`

Calls `service.sync_library()` and redraws the pages that show the library.
**Main thread.** It runs in two cases:

- when the All Songs page's Refresh button is clicked (given to
  `LibraryPage` as `on_rescan`);
- when `PlayerBar` tries to play a song whose file is gone, whether clicked
  in the library or selected by shuffle (`on_missing`).

| | |
|---|---|
| **Returns** | `None`. |
| **Raises** | Any error raised by `MusicService.sync_library` or its underlying library call. |

Redraws the All Songs and Downloads pages. Must run on the main thread,
because the library can only be used on the thread that created it.

---

### `app.enable_double_buffering()`

Asks Windows to draw the window off-screen first, which reduces flicker
while scrolling and resizing. Called once, 100 ms after the window is
built. **Main thread.** Windows only.

| | |
|---|---|
| **Returns** | `None`. |
