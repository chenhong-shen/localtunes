# LocalTunes

A desktop music player for Windows, written in Python. It plays the MP3s in a
local `Music` folder, and you can search YouTube from inside the app and
download a song's audio straight into your library.

## Features

- **Library:** every song in the `Music` folder, with the title and artist read
  from the file's tags. Songs you add or delete while the app is closed get
  picked up the next time it starts.
- **Playlists:** right-click any song to add it to a playlist or start a new
  one. Playlists can be played, renamed, and deleted, and songs can be removed
  from them.
- **Search and download:** search YouTube or paste a video link, then download
  the audio as an MP3. The Downloads page keeps a history of everything you've
  downloaded.
- **Playback:** play/pause, a seek bar, volume, and shuffle.
- **Settings:** light, dark, or system theme, volume, and how many search
  results to show.

## Setup

You'll need Windows and Python 3.

1. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Put `ffmpeg.exe` and `ffprobe.exe` in the `bin` folder. They aren't in the
   repo, but Windows builds are linked from [ffmpeg.org](https://ffmpeg.org/download.html).
   yt-dlp uses them to turn downloads into MP3s.

3. Search uses the YouTube Data API. Copy `.env.example` to `.env` and replace
   `YOUR_KEY_HERE` with your own API key, which you can create in the Google
   Cloud Console.

4. Run it:

   ```
   python main.py
   ```

Songs are saved to `Music/`, the library to `library.db`, and your settings to
`settings.json`, all in the same folder as `main.py`.

## How it's organized

`main.py` builds the window and connects everything. Each page (All Songs,
Playlists, Search, Downloads, Settings) and the player bar at the bottom live in
`ui/`. The pages don't touch the database or YouTube directly. They go through
`MusicService` in `music_service.py`, which calls the backend modules:

- `library.py`: the SQLite database of songs and playlists
- `search.py` and `downloader.py`: YouTube search and audio downloads
- `player.py` and `play_queue.py`: playback with pygame, and the play order for
  shuffle
- `paths.py`, `settings.py`, `thumbnails.py`, `formatting.py`: smaller helpers

Searches and downloads run on background threads so the window doesn't freeze
while they work. The `docs/` folder has a short write-up of each module's
interface.

Only download music you have the right to download.
