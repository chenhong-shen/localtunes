# thumbnails.py API

Version 2.0.0

Saving and loading song thumbnails. Thumbnails are saved in
`THUMBNAIL_FOLDER`, one per source, at `thumbnail_path(platform, source_id)`.

Songs are identified here by `(platform, source_id)`, as described in the
`library.py` API, not by their library `id`. A song that is removed and
added again gets a new `id` but keeps its source, so it finds its thumbnail
again. Songs without a `source_id` (local songs) never have a thumbnail.

## Module functions

### `save_thumbnail(platform, source_id)`

Downloads a video's 320x180 thumbnail from YouTube and saves it, creating
`THUMBNAIL_FOLDER` if needed. Replaces any thumbnail already saved for that
source. Slow: it makes a network request, so it should not be called on the
UI thread.

| | |
|---|---|
| `platform` (`str`) | The song's platform. Only `'youtube'` is supported: the picture is always fetched from YouTube. |
| `source_id` (`str`) | A YouTube video ID. Must not be `None`. |
| **Returns** | `None`. |
| **Raises** | `requests.RequestException` if the image cannot be downloaded, including when YouTube has no thumbnail for `source_id`. `OSError` if it cannot be saved. |

The 320x180 size is already 16:9, so the picture has no black bars.

```python
save_thumbnail("youtube", "ZU4eX9a6f7M")
```

---

### `load_thumbnail(platform, source_id, size)`

Loads a saved thumbnail for display. **Main thread.**

| | |
|---|---|
| `platform` (`str`) | The song's platform. |
| `source_id` (`str` or `None`) | The song's ID on that platform. |
| `size` (`tuple` of `int`) | The display size, as `(width, height)` in pixels. |
| **Returns** | `CTkImage`, or `None` if `source_id` is `None`, no thumbnail is saved for this source, or the file is not a readable image. |
| **Raises** | Nothing. |

The same picture is used in light and dark mode.

```python
load_thumbnail(song["platform"], song["source_id"], size=(160, 90))
```
