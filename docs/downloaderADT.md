# downloader.py API

Version 2.0.0

Downloads the audio of one video, using yt-dlp, and converts it to mp3 with
ffmpeg. `Download` only downloads and converts. It does not search, record
the song in the library, or save a thumbnail.

## Identifiers

A download is described by the video's URL, the folder to save it in, and
the folder holding ffmpeg. It is not identified by anything else.

The saved file is named `<title> [<video id>].mp3`, where the title and
video ID come from the site. Because the video ID is part of the name, two
different videos never share a filename, even if their titles are the same.
Characters that are not allowed in Windows filenames are replaced by yt-dlp,
so the filename may differ slightly from the title (for example, `|`
becomes `｜`).

The `[<video id>]` part of the name is relied on by `Library.sync`, which
reads it back to find the `source_id` of a file that is not in the library.
Without it, a downloaded song found by `sync` would be treated as a local
file. It must not be removed from the filename format.

## class `Download`

One video's audio, to be saved as an mp3 in one folder.

A `Download` does nothing until `download_youtube()` is called. It does not
change `url`, `folder`, or `ffmpeg_folder` after it is created.

---

### `Download(url, folder, ffmpeg_folder)`

Constructor. Prepares a download.

| | |
|---|---|
| `url` (`str`) | The video's URL, for example `'https://www.youtube.com/watch?v=BaW_jenozKc'`. Must be non-empty. |
| `folder` (`str`) | The folder to save the mp3 in. Created when the download runs if it does not exist. |
| `ffmpeg_folder` (`str`) | The folder holding `ffmpeg.exe` and `ffprobe.exe`. Not checked here; a missing ffmpeg is only noticed when the download runs. |
| **Returns** | `Download`. A download that has not run yet. |
| **Raises** | `TypeError` if `url` is not a `str`. `ValueError` if `url` is empty. |

```python
path = Download("https://www.youtube.com/watch?v=BaW_jenozKc", MUSIC_FOLDER, FFMPEG_FOLDER).download_youtube()
```

---

### `download.download_youtube()`

Downloads the video's best available audio into `folder`, converts it to
mp3, and writes the video's details into the file's tags. Slow: it makes
network requests, writes files, and runs ffmpeg, so it should not be called
on the UI thread.

| | |
|---|---|
| **Returns** | `str`. The full path of the saved `.mp3` file. |
| **Raises** | Errors from yt-dlp or ffmpeg when fetching or converting the audio, filesystem errors while writing it, and unexpected response-shape errors can propagate. They are not caught, so the caller can report them. |

The audio is always converted to **mp3 at 192 kbps**. The original
download (such as `webm` or `m4a`) is deleted after conversion, so only the
`.mp3` is left in `folder`.

The `FFmpegMetadata` postprocessor writes available video metadata into the
mp3's tags. Exact tags vary by source. Common metadata includes:

| Tag | Comes from |
|---|---|
| `title` | The video's title. |
| `artist` | Available artist or uploader metadata. It may differ from the channel title returned by YouTube search. |
| `date` | The upload date. |

`Download` itself does not check the library or prevent duplicate downloads.
The Search page checks for an existing library entry and an in-progress
download before starting this operation; callers that bypass that page must
provide their own duplicate handling.
