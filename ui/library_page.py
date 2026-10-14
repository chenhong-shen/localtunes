"""
The All Songs page: every downloaded song as a grid of boxes.
"""

import customtkinter as ctk

from thumbnails import load_thumbnail
from ui import plain
from ui.page import Page


# How many song boxes fit side by side.
LIBRARY_COLUMNS = 3


class LibraryPage(Page):
	"""A song count, a Rescan button, and a grid of song boxes, newest first.

	Layout, top to bottom:
		count of songs                                  [ Rescan ]
		scrollable grid of song boxes

	Clicking a box calls `on_play` with that song's library entry, so this
	page doesn't need to know anything about the player. Clicking Rescan
	calls `on_rescan()`; the app is expected to resync and call refresh().
	"""

	def __init__(self, parent, title, title_font, nav_font, service, on_play, on_rescan):
		super().__init__(parent, title, title_font)
		self.service = service
		self.on_play = on_play
		self.on_rescan = on_rescan

		# Toolbar row: the song count on the left, Rescan on the right. Same
		# layout as the Downloads page's toolbar.
		toolbar = ctk.CTkFrame(self, fg_color="transparent")
		toolbar.pack(fill="x", pady=(0, 8))

		# "12 songs", under the page title.
		self.count_label = ctk.CTkLabel(toolbar, text="", text_color="gray", anchor="w")
		self.count_label.pack(side="left")

		# No refresh here: on_rescan redraws this page itself.
		ctk.CTkButton(toolbar, text="Refresh", height=40, font=nav_font,
					  command=self.on_rescan).pack(side="right")

		

		# The boxes go in here. It scrolls once there are more than fit.
		self.grid_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
		self.grid_frame.pack(fill="both", expand=True)

		# Give every column the same share of the width, so the boxes stay
		# evenly sized. uniform="col" makes all columns exactly equal.
		for column in range(LIBRARY_COLUMNS):
			self.grid_frame.grid_columnconfigure(column, weight=1, uniform="col")

		self.refresh()

	def refresh(self):
		"""Redraws the grid of song boxes from the current history.

		MAIN THREAD. Called once when the page is built, and again after
		every successful download.
		"""
		for widget in self.grid_frame.winfo_children():
			widget.destroy()

		songs = self.service.get_history()   # newest first

		count = len(songs)
		self.count_label.configure(text=f"{count} song{'' if count == 1 else 's'}")

		if not songs:
			# grid, not pack, because the boxes below use grid in this frame.
			ctk.CTkLabel(self.grid_frame, text="No songs yet. Download some from Search.",
						 text_color="gray").grid(row=0, column=0, columnspan=LIBRARY_COLUMNS, pady=16)
			return

		# Place the boxes left to right, wrapping to a new row every
		# LIBRARY_COLUMNS songs. divmod(7, 3) gives (2, 1): song number 7 goes
		# in row 2, column 1.
		for index, song in enumerate(songs):
			row, column = divmod(index, LIBRARY_COLUMNS)
			box = self.make_song_box(song)
			box.grid(row=row, column=column, padx=6, pady=6, sticky="nsew")

	


	def make_song_box(self, song):
		"""Builds one song box and returns it (not placed).

		Layout, top to bottom:
			thumbnail (16:9)
			song name (bold, up to two lines)
			artist (gray)

		`song` is a library entry, with at least 'platform', 'source_id',
		'title', and 'artist'.
		"""
		# Card-colored frame with plain labels, so the grid scrolls with less
		# flickering (see ui/plain.py).
		box = plain.card(self.grid_frame, corner_radius=10)

		# --- Picture ---
		# 160x90 keeps YouTube's 16:9 shape.
		image = load_thumbnail(song["platform"], song["source_id"], size=(160, 90))
		if image is not None:
			ctk.CTkLabel(box, image=image, text="").pack(padx=8, pady=(8, 6))
		else:
			# No saved picture: a gray box the same size, with a music note,
			# so every box in the grid still lines up.
			ctk.CTkLabel(box, text="♪", width=160, height=90, corner_radius=6,
						 fg_color=("gray80", "gray25"), text_color="gray",
						 font=ctk.CTkFont(size=32)).pack(padx=8, pady=(8, 6))

		# --- Song name ---
		# Very long titles are cut so every box is a similar height.
		title = song["title"]
		if len(title) > 60:
			title = title[:57].rstrip() + "…"
		plain.label(box, title, size=13, bold=True, wraplength=160, cursor="hand2"
					).pack(fill="x", padx=10)

		# --- Artist ---
		plain.label(box, song["artist"], size=13, muted=True, wraplength=160, cursor="hand2"
					).pack(fill="x", padx=10, pady=(0, 10))

		# --- Make the whole box clickable ---
		# Frames have no command=, so bind a left click instead. Clicks on a
		# label inside the box don't reach the box itself, so every widget
		# inside it is bound too. s=song freezes this box's song.
		# (Plain labels don't inherit the box's cursor, so they set their own.)
		box.configure(cursor="hand2")
		for widget in [box] + box.winfo_children():
			widget.bind("<Button-1>", lambda e, s=song: self.on_play(s))

		return box
