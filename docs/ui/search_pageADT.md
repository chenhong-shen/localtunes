# ui/search_page.py API

Version 3.1.0

The Search page: searching YouTube, downloading search results, and
downloading a YouTube URL entered in the search box. `SearchPage` uses the
injected `MusicService` for search, URL metadata, downloads, duplicate checks,
and library recording. The page owns worker threads and UI event handling.

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
  widgets or use the SQLite library.
- **Worker threads** run slow work: searching, resolving URL metadata, and
  downloading. A worker never touches a widget or SQLite. It calls the service
  for search, metadata, or download work and reports its outcome through the
  page's event queue.

For a direct URL, one worker resolves metadata first. `poll_events()` checks
the resolved track against the library and the `downloading` set on the main
thread. If it is not a duplicate, the page adds its `(platform, source_id)`
key to the set and starts a second worker to download it.

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
| `"url_metadata_resolved"` | URL result `dict` with `platform`, `source_id`, `title`, `artist`, and `url` | `url_download` | Checks for a library or in-progress duplicate; if new, adds its key to `downloading` and starts `url_download_worker`. |
| `"url_metadata_error"` | `(url, str)`. The second item is the error message. | `url_download` | Shows the URL metadata error and re-enables Search. No download key has been added. |
| `"download_done"` | `(result, button, filepath)`. `filepath` is the full path of the saved song. | `download_worker` | Marks the song as no longer downloading, tries `service.record_download`, then calls `on_library_changed()` and shows success. If recording fails, shows an error and re-enables the button. |
| `"download_error"` | `(result, button, str)`. The last item is the error message. | `download_worker` | Marks the song as no longer downloading, shows the error, resets the button to + so the download can be retried. |
| `"url_download_done"` | `(result, filepath)` | `url_download_worker` | Removes the result key from `downloading`, records the download, calls `on_library_changed()`, shows success, and re-enables Search. If recording fails, shows an error and re-enables Search. |
| `"url_download_error"` | `(result, str)`. The second item is the error message. | `url_download_worker` | Removes the result key from `downloading`, shows the error, and re-enables Search. |

Each worker sends exactly one message for its task. URL metadata resolution and
URL audio download are separate worker tasks and use separate events.

## class `SearchPage`

A search bar, a status line, and one card per result. Subclass of `Page`.

Layout, top to bottom:

```
[ platform v ] [ search entry ........ ] [ Search ]
status line ("Searching...", "5 results", errors)
scrollable results area (one card per result)
```

The `downloading` set prevents duplicate requests for the same
`(platform, source_id)` while this page is open, including requests started
from a search result and from a direct URL. Successful downloads are recorded
by the service on the main thread. If recording fails, the completed audio
file remains on disk and the UI reports the library error.

---

### `SearchPage(parent, title, title_font, nav_font, service, on_library_changed)`

Constructor. Builds the page and starts checking the event queue.
**Main thread.**

| | |
|---|---|
| `parent` | The widget the page belongs in. |
| `title` (`str`) | The page title. |
| `title_font` (`CTkFont`) | The font for the page title. |
| `nav_font` (`CTkFont`) | The font for the Search button. |
| `service` (`MusicService`) | Handles search, downloading, duplicate checks, and recording completed downloads. |
| `on_library_changed` (function) | Called on the main thread after a successful record so the app can refresh library views. |
| **Returns** | `SearchPage`. A page with no results. |

The only platform currently offered is `"YouTube"`. Pressing Enter in the
search box has the same effect as clicking Search.

---

### `page.on_search()`

Starts either a catalog search or a direct URL download, depending on the
search-box contents. Called when Search is clicked or Enter is pressed.
**Main thread.**

| | |
|---|---|
| **Returns** | `None`. Returns immediately; the outcome arrives later through the event queue. |

If the search box is empty, or holds only spaces, this does nothing.
If it contains a recognized YouTube URL, it disables Search and starts
`url_download` on a worker thread to resolve metadata. Otherwise it disables
Search and starts `search_worker` on a worker thread. Search is re-enabled
when the corresponding operation completes or reports an error.

---

### `page.is_youtube_url(value)`

Returns whether `value` is an HTTP or HTTPS URL whose hostname is one of the
YouTube hostnames recognized by the page. **Main thread.**

| | |
|---|---|
| `value` (`str`) | Text to inspect. |
| **Returns** | `bool`. |

This is a host/scheme check; it does not verify that the video exists or that
the URL points to a single video rather than a playlist.

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

### `page.url_download(url, platform)`

Resolves a direct URL into the standard result dictionary. **Worker thread.**

| | |
|---|---|
| `url` (`str`) | YouTube URL entered in the search box. |
| `platform` (`str`) | Platform identifier supplied by `on_search()`; currently `"youtube"`. |
| **Returns** | `None`. Sends exactly one event: `"url_metadata_resolved"` on success or `"url_metadata_error"` on failure. |
| **Raises** | Nothing. Metadata errors are caught and reported through the event queue. |

It calls `MusicService.get_url_metadata()`. It does not download audio or
access the library.

---

### `page.url_download_worker(result)`

Downloads a URL-resolved result. **Worker thread.**

| | |
|---|---|
| `result` (`dict`) | Resolved result in the standard result format. |
| **Returns** | `None`. Sends exactly one event: `"url_download_done"` on success, with the filepath, or `"url_download_error"` on failure. |
| **Raises** | Nothing. Download errors are caught and reported through the event queue. |

The worker does not access SQLite or widgets. The main thread adds the result
key to `downloading` before starting it and removes the key when either
download event is handled.

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

Asks `MusicService` to download one result into its configured music folder
and reports the outcome.
**Worker thread.**

| | |
|---|---|
| `result` (`dict`) | The result passed to `MusicService.download`. |
| `button` (`CTkButton`) | The card's + button. Not used by this method; it is passed through in the event so the main thread can update it. |
| **Returns** | `None`. Sends exactly one event: `"download_done"` on success, with the saved file's full path, or `"download_error"` on any failure. |
| **Raises** | Nothing. Every exception is caught and reported as a `"download_error"` event. |

`MusicService.download` also attempts to save the song's thumbnail. A failed
thumbnail does not count as a failed audio download: the service ignores the
thumbnail error and `"download_done"` is still sent.

---

### `page.poll_events()`

Applies every event waiting on the event queue, as described under
[Events](#events), then schedules itself to run again in 100 ms.
**Main thread.**

| | |
|---|---|
| **Returns** | `None`. |

Started once, by the constructor, and runs for the life of the page.
`service.record_download` is only called here, on the main thread, so the
SQLite connection stays on its creating thread. If recording fails, the page
shows the error and re-enables the button.

If a card's button was destroyed by a new search before its download
finished, the library and status line are still updated, but the button is
left alone.
