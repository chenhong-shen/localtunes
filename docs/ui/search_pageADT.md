# ui/search_page.py API

Version 2.0.0

The Search page: searching YouTube, and downloading results. `SearchPage`
uses `Search` to find videos, `Download` to download them, and
`save_thumbnail` to save their pictures. It does not record downloads in
the library itself: it hands each finished download to the `on_downloaded`
function it was given.

## Identifiers

Search results are identified by their position in the most recent search,
as described in the `search.py` API. Results from earlier searches are
discarded when a new search finishes.

Songs are identified by their `(platform, source_id)` pair, as described in
the `search.py` and `library.py` APIs. The same pair is used to check the
library, to track downloads in progress, and to name thumbnails.

Event messages are identified by their kind, a `str`. The valid kinds are
listed under [Events](#events).

## Threading model

`SearchPage` uses two kinds of thread:

- The **main thread** runs the app's main loop. It draws the window,
  handles clicks, and is the only thread that may create, read, or change
  widgets, or use the library.
- **Worker threads** run slow work: searching and downloading. A worker never
  touches a widget or the library. When it finishes, it puts exactly one
  message on the page's event queue and ends.

The main thread checks the event queue every 100 ms, in `poll_events()`, and
applies each message to the UI. This keeps the window responsive while
searches and downloads run.

Methods below are marked **main thread** or **worker thread**. Calling a
main-thread method from a worker, or touching a widget or the library from
a worker, is a precondition violation and may crash the app unpredictably.

## Events

Each message on the event queue is a `(kind, data)` tuple.

| Kind | `data` | Sent by | Effect in `poll_events()` |
|---|---|---|---|
| `"search_results"` | `list` of result `dict`s | `search_worker` | Shows the results and the result count, re-enables the Search button. |
| `"search_error"` | `str`. The error message. | `search_worker` | Shows the error, re-enables the Search button. |
| `"download_done"` | `(result, button, filepath)`. `filepath` is the full path of the saved song. | `download_worker` | Marks the song as no longer downloading, calls `on_downloaded(result, filepath)`, shows a success message, changes the button to ✓. |
| `"download_error"` | `(result, button, str)`. The last item is the error message. | `download_worker` | Marks the song as no longer downloading, shows the error, resets the button to + so the download can be retried. |

Each worker sends exactly one message: one of the two kinds for its task.

## class `SearchPage`

A search bar, a status line, and one card per result. Subclass of `Page`.

Layout, top to bottom:

```
[ platform v ] [ search entry ........ ] [ Search ]
status line ("Searching...", "5 results", errors)
scrollable results area (one card per result)
```

**Invariant:** a `(platform, source_id)` pair is never in both the library and the set of songs
currently downloading. A song moves from "downloading" to "in the library"
when its download succeeds, and leaves "downloading" when it fails. Because
of this, a song is never downloaded twice.

---

### `SearchPage(parent, title, title_font, nav_font, history, on_downloaded)`

Constructor. Builds the page and starts checking the event queue.
**Main thread.**

| | |
|---|---|
| `parent` | The widget the page belongs in. |
| `title` (`str`) | The page title. |
| `title_font` (`CTkFont`) | The font for the page title. |
| `nav_font` (`CTkFont`) | The font for the Search button. |
| `history` (`Library`) | The app's library. Only read, with `has`, to mark songs already downloaded. |
| `on_downloaded` (function) | Called as `on_downloaded(result, filepath)` on the main thread when a download finishes. `filepath` is the full path of the saved song. |
| **Returns** | `SearchPage`. A page with no results. |

The only platform currently offered is `"YouTube"`. Pressing Enter in the
search box has the same effect as clicking Search.

---

### `page.on_search()`

Starts a search for the text in the search box. Called when Search is
clicked or Enter is pressed. **Main thread.**

| | |
|---|---|
| **Returns** | `None`. Returns immediately; the result arrives later as a `"search_results"` or `"search_error"` event. |

If the search box is empty, or holds only spaces, this does nothing.
Otherwise it disables the Search button until the search finishes, so only
one search runs at a time, and starts `search_worker` on a new worker
thread.

---

### `page.search_worker(query, platform)`

Runs a search and reports the outcome. **Worker thread.**

| | |
|---|---|
| `query` (`str`) | The text to search for. Non-empty. |
| `platform` (`str`) | The platform to search. Currently only `"YouTube"` is supported. |
| **Returns** | `None`. Sends exactly one event: `"search_results"` on success, `"search_error"` on any failure, including an unsupported platform. |
| **Raises** | Nothing. Every exception is caught and reported as a `"search_error"` event. |

Requests at most 10 results.

---

### `page.show_results(results)`

Replaces the contents of the results area with one card per result.
**Main thread.**

| | |
|---|---|
| `results` (`list` of `dict`) | Results in the format returned by `Search.search_youtube()`. May be empty. |
| **Returns** | `None`. |

Each card shows the result's title and artist, and a round + button that
starts a download of that result. Results already in the library show a
disabled ✓ button instead. If `results` is empty, the results area shows
"No results found" instead.

Any cards from a previous search are destroyed, including cards whose
downloads are still running.

---

### `page.on_download(result, button)`

Starts downloading one result. Called when a card's + button is clicked.
**Main thread.**

| | |
|---|---|
| `result` (`dict`) | The result to download, in the format returned by `Search.search_youtube()`. |
| `button` (`CTkButton`) | The + button on that result's card. |
| **Returns** | `None`. Returns immediately; if a download starts, its outcome arrives later as a `"download_done"` or `"download_error"` event. |

What happens depends on the song:

- **Already in the library:** no download starts. `button` changes to a
  disabled ✓ and the status line says it is already downloaded.
- **Already downloading:** no download starts. The status line says it is
  already downloading.
- **Otherwise:** the song is marked as downloading, `button` is disabled and
  changes to "…", and `download_worker` starts on a new worker thread.

Downloads of different songs may run at the same time.

---

### `page.download_worker(result, button)`

Downloads one result into `MUSIC_FOLDER` and reports the outcome.
**Worker thread.**

| | |
|---|---|
| `result` (`dict`) | The result to download. Its `'url'` is passed to `Download`. |
| `button` (`CTkButton`) | The card's + button. Not used by this method; it is passed through in the event so the main thread can update it. |
| **Returns** | `None`. Sends exactly one event: `"download_done"` on success, with the saved file's full path, or `"download_error"` on any failure. |
| **Raises** | Nothing. Every exception is caught and reported as a `"download_error"` event. |

After a successful download, also saves the song's thumbnail with
`save_thumbnail(result["platform"], result["source_id"])`. A failed thumbnail does not count as a failed download:
the error is ignored and `"download_done"` is still sent.

---

### `page.poll_events()`

Applies every event waiting on the event queue, as described under
[Events](#events), then schedules itself to run again in 100 ms.
**Main thread.**

| | |
|---|---|
| **Returns** | `None`. |

Started once, by the constructor, and runs for the life of the page.
`on_downloaded` is only ever called here, on the main thread, so two
downloads that finish together never write to the library at the same
time, and the library is never used from a worker thread.

If a card's button was destroyed by a new search before its download
finished, the library and status line are still updated, but the button is
left alone.
