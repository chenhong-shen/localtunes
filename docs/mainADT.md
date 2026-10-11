# main.py API

Version 2.2.0

The LocalTunes main window. `App` builds the window and connects the pieces:
the pages, the player bar, the library, and the player. `App` does not
search, download, play, or store songs itself, and it does not draw any
page's contents. Each piece lives in its own file:

| File | Holds | Documented in |
|---|---|---|
| `ui/library_page.py` | `LibraryPage`: the All Songs grid | `ui/library_pageADT.md` |
| `ui/search_page.py` | `SearchPage`: searching and downloading | `ui/search_pageADT.md` |
| `ui/downloads_page.py` | `DownloadsPage`: the download list | `ui/downloads_pageADT.md` |
| `ui/player_bar.py` | `PlayerBar`: the playback bar | `ui/player_barADT.md` |
| `ui/page.py` | `Page`: the base class of every page | `ui/pageADT.md` |
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
When a page needs the `App` to do something, it calls a function it was
given (`on_play`, `on_rescan`, `on_downloaded`, `on_missing`).

#### State

| Attribute | Type | Meaning |
|---|---|---|
| `library` | `Library` | The app's one library, shared by every page. |
| `player` | `Player` | The app's one player, used by the player bar. |
| `player_bar` | `PlayerBar` | The playback bar. |
| `library_page` | `LibraryPage` | The All Songs page. |
| `search_page` | `SearchPage` | The Search page. |
| `downloads_page` | `DownloadsPage` | The Downloads page. |

---

### `App()`

Constructor. Opens the library at `LIBRARY_FILE` and syncs it with
`MUSIC_FOLDER`, creates the player, and builds the window, the player bar,
every page, and the sidebar. **Main thread.**

| | |
|---|---|
| **Returns** | `App`. A window showing the All Songs page. The window is not displayed until `mainloop()` is called. |
| **Raises** | Any error raised by `Library` while opening or syncing the library, for example if `LIBRARY_FILE` exists but is not an SQLite database, or `MUSIC_FOLDER` cannot be read. |

The library is synced before the pages are built, so each page's first
draw already shows the synced songs, and no page has to be drawn twice.

The player bar is built before the pages, because the All Songs page needs
its `play_song` method. The player bar is given `resync` as its
`on_missing` function, and the All Songs page is given it as `on_rescan`.
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

### `app.on_downloaded(result, filepath)`

Records a finished download in the library and redraws the pages that show
the library. Given to `SearchPage`, which calls it when a download finishes.
**Main thread.**

| | |
|---|---|
| `result` (`dict`) | The downloaded search result, in the format returned by `Search.search_youtube()`: it has the `'platform'`, `'source_id'`, `'title'`, `'artist'`, and `'url'` keys `Library.add` reads. |
| `filepath` (`str`) | The full path of the saved song. |
| **Returns** | `None`. |
| **Raises** | Any error raised by `Library.add`. |

Only the filename is stored in the library; `paths.song_path` rebuilds the
full path. Redraws the All Songs and Downloads pages.

Must run on the main thread, because the library can only be used on the
thread that created it.

---

### `app.resync()`

Syncs the library with `MUSIC_FOLDER` and redraws the pages that show the
library. **Main thread.** It runs in two cases:

- when the All Songs page's Rescan button is clicked (given to
  `LibraryPage` as `on_rescan`);
- when a song is clicked whose file is gone (given to `PlayerBar` as
  `on_missing`).

| | |
|---|---|
| **Returns** | `None`. |
| **Raises** | Any error raised by `Library.sync`. |

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
