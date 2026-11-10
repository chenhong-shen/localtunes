# ui/library_page.py API

Version 3.0.0

The All Songs page: every song in the library, as a grid of boxes, with a
Refresh button that resyncs the `Music` folder. `LibraryPage` reads songs through
`MusicService`. It does not play them or change the library: clicking a box
calls `on_play`, clicking Refresh calls `on_rescan`, and right-clicking a
box opens an Add to playlist menu.

## Module constants

### `LIBRARY_COLUMNS`

`int`. How many song boxes appear side by side: `3`.

## class `LibraryPage`

A song count, a Refresh button, and a scrollable grid of song boxes, newest
first. Subclass of `Page`.

Layout, top to bottom:

```
count of songs                                  [ Refresh ]
scrollable grid of song boxes
```

---

### `LibraryPage(parent, title, title_font, nav_font, service, on_play, on_rescan, on_playlists_changed)`

Constructor. Builds the page and draws the grid once. **Main thread.**

| | |
|---|---|
| `parent` | The widget the page belongs in. |
| `title` (`str`) | The page title. |
| `title_font` (`CTkFont`) | The font for the page title. |
| `nav_font` (`CTkFont`) | The font for the Refresh button. |
| `service` (`MusicService`) | Reads library history and owns library sync workflows. |
| `on_play` (function) | Called as `on_play(song)` when a song box is clicked. `song` is that song's library entry. |
| `on_rescan` (function) | Called as `on_rescan()`, with no arguments, when Refresh is clicked. Expected to sync through `MusicService` and refresh the library views. In the app, this is `App.resync`. |
| `on_playlists_changed` (function) | Called as `on_playlists_changed()` after a song is added to a playlist from the right-click menu. In the app, this is `PlaylistsPage.refresh`. |
| **Returns** | `LibraryPage`. A page showing the library's current songs. |

---

### `page.refresh()`

Redraws the grid of song boxes from the current library. Called once when
the page is built, and again after every successfully recorded download and
every resync. **Main thread.**

| | |
|---|---|
| **Returns** | `None`. |

Shows the number of songs (for example `"1 song"` or `"12 songs"`), then
one box per song in the library, newest first, `LIBRARY_COLUMNS` boxes per
row. If the library is empty, shows "No songs yet. Download some from
Search." instead.

---

### `page.make_song_box(song)`

Builds one song box. **Main thread.**

| | |
|---|---|
| `song` (`dict`) | A library entry, with at least the keys `'platform'`, `'source_id'`, `'title'`, and `'artist'`. |
| **Returns** | `CTkFrame`. The box, not yet placed; the caller places it. |

The box shows, top to bottom:

- the song's thumbnail at 160x90, or a gray placeholder with a ♪ of the
  same size if it has none (always the case for local songs), so every box
  lines up;
- its title in bold, shortened with "…" past 60 characters;
- its artist, in gray.

Clicking anywhere on the box calls `on_play(song)`. Right-clicking it calls
`show_song_menu`: a menu with Add to playlist > each playlist, and
New playlist… (which asks for a name and makes one). Adding a song that is
already in the playlist does nothing.

---

### `page.shuffle()`

No-op placeholder that returns `None`. It does not shuffle the library or
playback queue; shuffle is controlled by `PlayerBar.toggle_shuffle()`.
