# LocalTunes

A local desktop music player. The UI delegates library, search, download, and
sync workflows to `MusicService` (`music_service.py`). The service coordinates
the SQLite library with the search, downloader, and thumbnail modules.

Run the app with `python main.py`. See `docs/music_serviceADT.md` for the
service API and `docs/mainADT.md` for the application structure.
