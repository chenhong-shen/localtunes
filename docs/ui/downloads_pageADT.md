# ui/downloads_page.py API

Version 1.1.0

The Downloads page: a list of every song in the library, and a button to
open the `Music` folder. `DownloadsPage` only reads the library.

## class `DownloadsPage`

A count, an "Open folder" button, and one card per song. Subclass of `Page`.

Layout, top to bottom:

```
count of downloads                         [ Open folder ]
scrollable list (one card per song, newest first)
```

---

### `DownloadsPage(parent, title, title_font, nav_font, history)`

Constructor. Builds the page and draws the list once. **Main thread.**

| | |
|---|---|
| `parent` | The widget the page belongs in. |
| `title` (`str`) | The page title. |
| `title_font` (`CTkFont`) | The font for the page title. |
| `nav_font` (`CTkFont`) | The font for the "Open folder" button. |
| `history` (`Library`) | The app's library. Only read. |
| **Returns** | `DownloadsPage`. A page showing the library's current songs. |

---

### `page.refresh()`

Redraws the list from the current library. Called once when the page is
built, and again after every successful download. **Main thread.**

| | |
|---|---|
| **Returns** | `None`. |

Shows the number of songs (for example `"1 download"` or `"5 downloads"`),
then one card per song, newest first, with the title on the first line and
`"<artist>  ·  <date>"` on the second. The date is formatted with
`format_date`. If the library is empty, the list shows "No downloads yet"
instead.

Every song in the library is listed, including songs added by
`Library.sync` that were not downloaded through the app.

---

### `page.open_folder()`

Opens `MUSIC_FOLDER` in File Explorer, creating it first if it does not
exist. Called when "Open folder" is clicked. **Main thread.** Windows only.

| | |
|---|---|
| **Returns** | `None`. |
| **Raises** | `OSError` if the folder cannot be created or opened. |
