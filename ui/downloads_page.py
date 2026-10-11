"""
The Downloads page: the download history, and a button to open the folder.
"""

import os
import customtkinter as ctk

from formatting import format_date
from paths import MUSIC_FOLDER
from ui import plain
from ui.page import Page




class DownloadsPage(Page):
	"""A count, an "Open folder" button, and one card per download.

	Layout, top to bottom:
		count of downloads                         [ Open folder ]
		scrollable list (one card per download, newest first)
	"""

	def __init__(self, parent, title, title_font, nav_font, history):
		super().__init__(parent, title, title_font)
		self.history = history
		self.nav_font = nav_font

		# Toolbar row: the download count on the left, the button on the right.
		toolbar = ctk.CTkFrame(self, fg_color="transparent")
		toolbar.pack(fill="x", pady=8)

		self.count_label = ctk.CTkLabel(toolbar, text="", text_color="gray", anchor="w")
		self.count_label.pack(side="left")

		ctk.CTkButton(toolbar, text="Open folder", height=40, font=nav_font,
					  command=self.open_folder).pack(side="right")

		# Where the download cards go.
		self.list_frame = ctk.CTkScrollableFrame(self)
		self.list_frame.pack(fill="both", expand=True)

		self.refresh()

	def refresh(self):
		"""Redraws the download list from the current history.

		MAIN THREAD. Called once when the page is built, and again after
		every successful download.
		"""
		for widget in self.list_frame.winfo_children():
			widget.destroy()

		entries = self.history.get_download_history()   # newest first

		# Singular vs plural, so it reads "1 download" and "5 downloads".
		count = len(entries)
		self.count_label.configure(text=f"{count} download{'' if count == 1 else 's'}")

		if not entries:
			ctk.CTkLabel(self.list_frame, text="No downloads yet",
						 text_color="gray").pack(pady=16)
			return

		for entry in entries:
			# A flat card with plain labels, so the list scrolls without
			# flickering (see ui/plain.py).
			card = plain.card(self.list_frame)
			card.pack(fill="x", pady=4, padx=4)
			card.grid_columnconfigure(0, weight=1)

			plain.label(card, entry["title"], size=14, wraplength=400
						).grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 0))

			# Second line: "Artist · Oct 8, 10:35 PM"
			subtitle = f"{entry['artist']}  ·  {format_date(entry['downloaded_at'])}"
			plain.label(card, subtitle, size=13, muted=True
						).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

	def open_folder(self):
		"""Opens the Music folder in File Explorer, creating it if needed.

		os.startfile is Windows-only.
		"""
		os.makedirs(MUSIC_FOLDER, exist_ok=True)
		os.startfile(MUSIC_FOLDER)