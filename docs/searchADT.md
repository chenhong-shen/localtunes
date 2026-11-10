# search.py API

Version 2.0.0

## Identifiers

Results are identified by their platform and source ID, the same pair the
library uses (see the `library.py` API). For YouTube, `platform` is
`'youtube'` and `source_id` is the 11-character video ID assigned by
YouTube (for example, `'BaW_jenozKc'`). It is unique per video. The same
video can have many URLs, but only one video ID.

Search results are identified by their position in the list returned
by `search_youtube()`. Positions are zero-based and contiguous: a search
returning n results uses positions 0 through n-1. Position 0 is the
top-ranked result. Positions are only meaningful within a single
search, and a new search starts numbering again at 0.

A search is not identified by anything. It is described by its
`query` and `max_results`.

The `url` is derived from the video ID and is not an identifier.

## class `Search`

A YouTube search. `Search` only finds videos and reports their URLs and other
relevant data. It does not download anything or handle any other part of the
app.

The search methods do not change `query` or `max_results`. They are ordinary
Python attributes, however, so callers can assign to them directly. The list
and dictionaries returned by `search_youtube()` are newly created, so the
caller may modify those results.

---

### `Search(query, max_results)`

Constructor. Creates a search for a query.

| | |
|---|---|
| `query` (`str`) | What to search for. Leading and trailing whitespace is removed; the remaining text must be non-empty. |
| `max_results` (`int`) | Maximum number of results to return. Must be an integer from 1 to 50 (the most the YouTube API returns); `bool` is rejected. |
| **Returns** | `Search`. A search that has not been executed yet. |
| **Raises** | `TypeError` if `query` is not a `str`, or if `max_results` is not an integer (including `bool`). `ValueError` if the stripped query is empty or `max_results` is outside 1 to 50. |

---

### `search.search_youtube()`

Searches YouTube through the Google YouTube Data API for videos related
to the query. The module loads `ENV_FILE` from `paths.py` with python-dotenv;
the request reads `YT_API_KEY` from the process environment and uses a
10-second timeout.

| | |
|---|---|
| **Returns** | `list` of `dict`. One dict per result, in YouTube's ranking order. May hold fewer than `max_results` entries, or be empty. A fresh list, safe to modify. |
| **Raises** | `KeyError` if `YT_API_KEY` is not set. `requests.RequestException` for a network timeout/failure or non-success HTTP status. JSON decoding or unexpected response-shape errors also propagate. |

Each dict has exactly these keys, which are the keys `Library.add` reads:

```python
{
    "platform": "youtube",
    "source_id": "BaW_jenozKc",
    "title": "Example video title",
    "artist": "Example Channel",
    "url": "https://www.youtube.com/watch?v=BaW_jenozKc",
}
```

| Key | Meaning |
|---|---|
| `'platform'` | Always `'youtube'`. |
| `'source_id'` | The video ID. |
| `'title'` | The video's title, with HTML escapes such as `&amp;` turned back into characters. |
| `'artist'` | The channel that uploaded the video, unescaped the same way. |
| `'url'` | The video's page, built from the video ID. |

A result has no `'filepath'` or `'downloaded_at'`: those only exist once
the song has been downloaded and added to the library.
