"""
Where LocalTunes keeps its files.

Everything is placed next to the app itself (next to main.py when run from
source, next to the .exe when built with PyInstaller), so it works no matter
which folder the app is launched from.
"""

import os
import sys


if getattr(sys, "frozen", False):
	APP_DIR = os.path.dirname(sys.executable)
else:
	APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Downloaded songs. Passed to Download, so the downloader and the rest of the
# app always agree on where the music is.
MUSIC_FOLDER = os.path.join(APP_DIR, "Music")

# Song thumbnails, one per song, named <platform>_<source_id>.jpg.
THUMBNAIL_FOLDER = os.path.join(APP_DIR, "thumbnails")

# The library file. Passed to Library.
LIBRARY_FILE = os.path.join(APP_DIR, "library.db")

# ffmpeg.exe and ffprobe.exe. Passed to Download.
FFMPEG_FOLDER = os.path.join(APP_DIR, "bin")

# .env file, passed to Search
ENV_FILE = os.path.join(APP_DIR, ".env")


def song_path(filename):
	"""Returns the full path to a downloaded song, given its filename.

	The history stores only filenames (not full paths), so it keeps working
	if the app folder is moved. Use this to turn one back into a real path.
	"""
	return os.path.join(MUSIC_FOLDER, filename)


def thumbnail_path(platform, source_id):
	"""Returns where the thumbnail for a song is (or would be) saved, given
	its platform and source ID. The file is named after the source, not the
	song's library number, so a song that is removed and added again finds
	its picture again.
	"""
	return os.path.join(THUMBNAIL_FOLDER, f"{platform}_{source_id}.jpg")