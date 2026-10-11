# ui/downloads_page.py API

Version 2.0.0

The Downloads page: a list of non-local songs in the library's download
history, and a button to open the `Music` folder. `DownloadsPage` reads this
history through `MusicService`.

## class `DownloadsPage`

A count, an "Open folder" button, and one card per non-local song. Subclass
of `Page`.

Layout, top to bottom:

```
count of downloads                         [ Open folder ]
scrollable list (one card per song, newest first)
```

---

### `DownloadsPage(parent, title, title_font, nav_font, service)`

Constructor. Builds the page and draws the list once. **Main thread.**

| | |
|---|---|
| `parent` | The widget the page belongs in. |
| `title` (`str`) | The page title. |
| `title_font` (`CTkFont`) | The font for the page title. |
| `nav_font` (`CTkFont`) | The font for the "Open folder" button. |
| `service` (`MusicService`) | Reads the library's download history. |
| **Returns** | `DownloadsPage`. A page showing the library's current songs. |

---

### `page.refresh()`

Redraws the list from the current library. Called once when the page is
built, and again after every successfully recorded download. **Main thread.**

| | |
|---|---|
| **Returns** | `None`. |

Shows the number of songs (for example `"1 download"` or `"5 downloads"`),
then one card per non-local song, newest first, with the title on the first line and
`"<artist>  ·  <date>"` on the second. The date is formatted with
`format_date`. If the library is empty, the list shows "No downloads yet"
instead.

YouTube entries discovered by `Library.sync` are included. Local entries
discovered by `sync` are excluded because `Library.get_download_history`
filters out rows whose platform is `'local'`.

---

### `page.open_folder()`

Opens `MUSIC_FOLDER` in File Explorer, creating it first if it does not
exist. Called when "Open folder" is clicked. **Main thread.** Windows only.

| | |
|---|---|
| **Returns** | `None`. |
| **Raises** | `OSError` if the folder cannot be created or opened. |
