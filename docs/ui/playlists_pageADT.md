# ui/playlists_page.py API

Version 1.0.0

The Playlists page: every playlist, and the songs in one playlist.
`PlaylistsPage` reads and changes playlists through `MusicService`. It does
not play anything: playing calls `on_play_playlist`. Songs are added to
playlists from the All Songs page (right-click a song).

## class `PlaylistsPage`

Subclass of `Page`. Two views, swapped by `refresh()`:

```
List view                                Detail view
count of playlists   [ New playlist ]    [ ← Back ]  name   [ Delete ] [ Rename ] [ ▶ Play ]
one card per playlist (newest first)     count of songs
                                         one card per song (playlist order), each with ✕
```

Every method runs on the **main thread**.

#### State

| Attribute | Type | Starts as | Meaning |
|---|---|---|---|
| `open_playlist` | `int` or `None` | `None` | `None` shows the list view; a playlist `id` shows that playlist. If the playlist no longer exists, `refresh()` goes back to the list view. |

---

### `PlaylistsPage(parent, title, title_font, nav_font, service, on_play_playlist)`

Constructor. Builds the page and draws the list view once.

| | |
|---|---|
| `parent` | The widget the page belongs in. |
| `title` (`str`) | The page title. |
| `title_font` (`CTkFont`) | The font for the page title. |
| `nav_font` (`CTkFont`) | The font for the buttons. |
| `service` (`MusicService`) | Reads and changes playlists. |
| `on_play_playlist` (function) | Called as `on_play_playlist(playlist_id)` when Play is clicked, and as `on_play_playlist(playlist_id, start=song)` when a song in the detail view is clicked. In the app, this is `PlayerBar.play_playlist`. |
| **Returns** | `PlaylistsPage`. |

---

### `page.refresh()`

Redraws whichever view is showing, from the current playlists. Called after
every change made on the page, and by the app after a song is added to a
playlist, after a download, and after a resync.

### `page.open(playlist_id)` / `page.back()`

Switch to the detail view of one playlist, or back to the list view.

### Actions

| Control | What happens |
|---|---|
| New playlist | Asks for a name. Blank or cancelled does nothing. |
| A playlist card | `open(id)`. |
| ▶ Play | `on_play_playlist(id)`. Disabled while the playlist is empty. |
| A song card | `on_play_playlist(id, start=song)`. |
| ✕ on a song | Removes the song from the playlist (not from the library). |
| Rename | Asks for a new name. Blank or cancelled does nothing. |
| Delete | Asks to confirm, then deletes the playlist (its songs stay in the library) and goes back to the list. |
