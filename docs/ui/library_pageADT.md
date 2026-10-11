# ui/library_page.py API

Version 2.0.0

The All Songs page: every song in the library, as a grid of boxes, with a
button to rescan the `Music` folder. `LibraryPage` only shows songs. It
does not play them or change the library: clicking a box calls the
`on_play` function it was given, and clicking Rescan calls `on_rescan`.

## Module constants

### `LIBRARY_COLUMNS`

`int`. How many song boxes appear side by side: `3`.

## class `LibraryPage`

A song count, a Rescan button, and a scrollable grid of song boxes, newest
first. Subclass of `Page`.

Layout, top to bottom:

```
count of songs                                  [ Rescan ]
scrollable grid of song boxes
```

---

### `LibraryPage(parent, title, title_font, nav_font, history, on_play, on_rescan)`

Constructor. Builds the page and draws the grid once. **Main thread.**

| | |
|---|---|
| `parent` | The widget the page belongs in. |
| `title` (`str`) | The page title. |
| `title_font` (`CTkFont`) | The font for the page title. |
| `nav_font` (`CTkFont`) | The font for the Rescan button. |
| `history` (`Library`) | The app's library. Only read. |
| `on_play` (function) | Called as `on_play(song)` when a song box is clicked. `song` is that song's library entry. |
| `on_rescan` (function) | Called as `on_rescan()`, with no arguments, when Rescan is clicked. Expected to sync the library and call this page's `refresh()`; the page does not redraw itself afterwards. In the app, this is `App.resync`. |
| **Returns** | `LibraryPage`. A page showing the library's current songs. |

---

### `page.refresh()`

Redraws the grid of song boxes from the current library. Called once when
the page is built, and again after every successful download and every
resync. **Main thread.**

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

Clicking anywhere on the box calls `on_play(song)`.
