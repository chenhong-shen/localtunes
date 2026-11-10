"""
LocalTunes: the main window.

This file only builds the window and connects the pieces. Each part of the
screen lives in its own file:

	ui/library_page.py    -> LibraryPage: the All Songs grid
	ui/playlists_page.py  -> PlaylistsPage: playlists and their songs
	ui/search_page.py     -> SearchPage: searching and downloading
	ui/downloads_page.py  -> DownloadsPage: the download history
	ui/settings_page.py   -> SettingsPage: theme, volume and search options
	ui/player_bar.py      -> PlayerBar: the playback bar at the bottom
	music_service.py      -> MusicService: app workflows between UI and backend modules

and the non-UI pieces have their own files too:

	search.py            -> Search: finds videos on YouTube
	downloader.py        -> Download: downloads a video's audio
	library.py           -> Library: Handles the database of songs 
	player.py            -> Player: plays one song
	paths.py             -> where every file is kept
	thumbnails.py        -> saving and loading song pictures
	formatting.py        -> turning times and dates into text
"""

import os
import customtkinter as ctk

from library import Library
from player import Player
from paths import LIBRARY_FILE, MUSIC_FOLDER, FFMPEG_FOLDER
from music_service import MusicService
import settings
from ui.settings_page import SettingsPage
from ui.library_page import LibraryPage
from ui.playlists_page import PlaylistsPage
from ui.search_page import SearchPage
from ui.downloads_page import DownloadsPage
from ui.player_bar import PlayerBar


class App(ctk.CTk):
	"""The LocalTunes main window.

	Layout:
		| sidebar | the current page          |   row 0 (stretches)
		|          player bar                 |   row 1

	Every page is placed in the same grid cell; clicking a sidebar button
	raises that page to the front.
	"""

	def __init__(self):
		super().__init__()
		self.title("LocalTunes")
		self.geometry("800x600")

		# Column 1 (the pages) and row 0 (everything but the player bar) take
		# up the extra space when the window grows.
		self.grid_columnconfigure(1, weight=1)
		self.grid_rowconfigure(0, weight=1)

		# Created once and passed to the pages, so every title and button matches.
		self.title_font = ctk.CTkFont(family="Segoe UI Variable Display", size=20, weight="bold")
		self.nav_font = ctk.CTkFont(family="Segoe UI Variable Text", size=14)

		# --- Shared state ---
		# One library/service and one player for the whole app.
		self.library = Library(LIBRARY_FILE)
		self.service = MusicService(self.library, MUSIC_FOLDER, FFMPEG_FOLDER)
		# Synced before the pages are built, so their first draw already
		# shows songs added or deleted while the app was closed.
		self.service.sync_library()
		self.player = Player()

		# --- Settings ---
		# Applied before the pages are built, so they're drawn in the saved
		# theme and the first song plays at the saved volume.
		prefs = settings.load()
		ctk.set_appearance_mode(prefs["appearance"])
		self.player.set_volume(prefs["volume"])

		# --- Player bar ---
		# Built before the pages, because the All Songs page needs its
		# play_song method.
		self.player_bar = PlayerBar(self, self.player, on_missing=self.resync, service=self.service)
		self.player_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

		# --- Pages ---
		# Pages use the service for library/search/download operations. UI-only
		# actions are passed as callbacks instead of reaching into the App.
		# Playlists is built before All Songs, because All Songs redraws it
		# after a song is added to a playlist.
		self.playlists_page = PlaylistsPage(self, "Playlists", self.title_font, self.nav_font, self.service,
											on_play_playlist=self.player_bar.play_playlist)
		self.library_page = LibraryPage(self, "All Songs", self.title_font, self.nav_font, self.service,
										on_play=self.player_bar.play_from_library, on_rescan=self.resync,
										on_playlists_changed=self.playlists_page.refresh)
		self.search_page = SearchPage(self, "Search", self.title_font, self.nav_font, self.service,
									  on_library_changed=self.refresh_library_views)
		self.downloads_page = DownloadsPage(self, "Downloads", self.title_font, self.nav_font, self.service)
		# A theme change redraws the pages built from plain labels, which
		# keep the colors they were created with (see ui/plain.py).
		self.settings_page = SettingsPage(self, "Settings", self.title_font, self.nav_font,
										  self.service, self.player,
										  on_appearance_changed=self.refresh_library_views)

		# (sidebar text, page) in sidebar order.
		nav = [
			("All Songs", self.library_page),
			("Playlists", self.playlists_page),
			("Search", self.search_page),
			("Downloads", self.downloads_page),
			("Settings", self.settings_page),
		]

		# Every page goes in the same cell; show() decides which is on top.
		for _, page in nav:
			page.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)

		# --- Sidebar ---
		sidebar = ctk.CTkFrame(self, width=160, corner_radius=0)
		sidebar.grid(row=0, column=0, sticky="ns")

		ctk.CTkLabel(sidebar, text="LocalTunes", font=self.title_font, fg_color=self.cget("fg_color"),
					 corner_radius=8, width=140, height=60).pack(padx=16, pady=16)

		# One button per page. p=page freezes this button's page; without it,
		# every button would open the last page in the loop.
		for label, page in nav:
			ctk.CTkButton(sidebar, text=label, font=self.nav_font, height=40,
						  command=lambda p=page: self.show(p)).pack(padx=16, pady=8, fill="x")

		

		#self.after(100, self.enable_double_buffering)

	

		self.show(self.library_page)   # the page the app opens on

	def show(self, page):
		"""Brings `page` to the front, hiding the others behind it."""
		page.tkraise()

	def refresh_library_views(self):
		"""Redraw pages after the service changes the library. MAIN THREAD."""
		self.library_page.refresh()
		self.downloads_page.refresh()
		self.playlists_page.refresh()

	def enable_double_buffering(self):
		# Ask Windows to draw the window off-screen first, to reduce flicker.
		import ctypes
		GWL_EXSTYLE = -20
		WS_EX_COMPOSITED = 0x02000000
		hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
		style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
		ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_COMPOSITED)

	def resync(self):
		"""Syncs the library with the Music folder and redraws the pages
		that show it. Called by PlayerBar when a song's file is missing.
		MAIN THREAD.
		"""
		self.service.sync_library()
		self.library_page.refresh()
		self.downloads_page.refresh()
		self.playlists_page.refresh()

if __name__ == "__main__":
	App().mainloop()
