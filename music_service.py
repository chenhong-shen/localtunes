"""Application workflows shared by the UI and the local music backend."""

import os

from downloader import Download
from search import Search
from thumbnails import save_thumbnail


class MusicService:
	"""Coordinates library, search, and download operations for the app.

	The library is created by the app and must only be accessed from the
	thread that created it. Search and download work may run on workers; those
	methods do not touch SQLite.
	"""

	def __init__(self, library, music_folder, ffmpeg_folder):
		self.library = library
		self.music_folder = music_folder
		self.ffmpeg_folder = ffmpeg_folder

	def sync_library(self):
		"""Reconcile library records with the files in the music folder."""
		self.library.sync(self.music_folder)

	def get_all_songs(self):
		return self.library.get_all_songs()

	def get_history(self, newest=True):
		return self.library.get_history(newest=newest)

	def get_download_history(self, newest=True):
		return self.library.get_download_history(newest=newest)

	def has_song(self, platform, source_id):
		return self.library.has(platform, source_id)

	def search(self, query, platform="YouTube", max_results=10):
		"""Search the configured catalog. Safe to call from a worker thread."""
		if platform != "YouTube":
			raise ValueError(f"Unsupported platform: {platform}")
		return Search(query=query, max_results=max_results).search_youtube()

	def download(self, result):
		"""Download one search result and attempt to save its thumbnail.

		Safe to call from a worker thread. It does not access SQLite.
		"""
		filepath = Download(result["url"], self.music_folder,
							self.ffmpeg_folder).download_youtube()
		try:
			save_thumbnail(result["platform"], result["source_id"])
		except Exception:
			# A thumbnail is optional; a completed audio download remains valid.
			pass
		return filepath

	def record_download(self, result, filepath):
		"""Add a completed download to SQLite. Call on the library thread."""
		return self.library.add(result, os.path.basename(filepath), autocommit=True)
