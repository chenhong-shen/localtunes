"""
The Playlists page: every playlist, and the songs in one playlist.
"""

from tkinter import messagebox
import customtkinter as ctk

from ui import plain
from ui.page import Page


class PlaylistsPage(Page):
	"""Two views in one page, swapped by refresh():

	List view (open_playlist is None):
		count of playlists                        [ New playlist ]
		scrollable list (one card per playlist, newest first)

	Detail view (open_playlist is a playlist id):
		[ <- Back ]  name           [ Delete ] [ Rename ] [  Play ]
		count of songs
		scrollable list (one card per song, in playlist order, each with X

	Songs are added from the All Songs page (right-click a song). Playing is
	done through `on_play_playlist(playlist_id, start)`, so this page doesn't
	need to know anything about the player.
	"""

	def __init__(self, parent, title, title_font, nav_font, service, on_play_playlist):
		super().__init__(parent, title, title_font)
		self.service = service
		self.nav_font = nav_font
		self.on_play_playlist = on_play_playlist
		# Which view is showing: None = the list, else the open playlist's id.
		# An id (not the playlist dict) so a rename shows up on the next refresh.
		self.open_playlist = None

		# Both views are built inside this frame, so refresh() can clear it
		# without touching the page title.
		self.content = ctk.CTkFrame(self, fg_color="transparent")
		self.content.pack(fill="both", expand=True)

		self.refresh()

	def refresh(self):
		"""Redraws whichever view is showing. MAIN THREAD.

		Called when the page is built, after any change made on this page,
		and by the app after songs are added to a playlist, downloaded, or
		removed by a resync.
		"""
		for widget in self.content.winfo_children():
			widget.destroy()

		if self.open_playlist is None:
			self.show_list()
			return

		# The playlist may have been deleted since it was opened.
		playlist = self._find_playlist(self.open_playlist)
		if playlist is None:
			self.open_playlist = None
			self.show_list()
		else:
			self.show_detail(playlist)

	# --- List view ---

	def show_list(self):
		playlists = self.service.get_playlists()   # newest first

		toolbar = ctk.CTkFrame(self.content, fg_color="transparent")
		toolbar.pack(fill="x", pady=8)

		count = len(playlists)
		ctk.CTkLabel(toolbar, text=f"{count} playlist{'' if count == 1 else 's'}",
					 text_color="gray", anchor="w").pack(side="left")
		ctk.CTkButton(toolbar, text="New playlist", height=40, font=self.nav_font,
					  command=self.new_playlist).pack(side="right")

		list_frame = ctk.CTkScrollableFrame(self.content)
		list_frame.pack(fill="both", expand=True)

		if not playlists:
			ctk.CTkLabel(list_frame, text="No playlists yet. Make one here, or right-click\n"
						 "a song on All Songs and choose Add to playlist.",
						 text_color="gray").pack(pady=16)
			return

		for playlist in playlists:
			# Same flat card as the Downloads page (see ui/plain.py).
			card = plain.card(list_frame)
			card.pack(fill="x", pady=4, padx=4)

			plain.label(card, playlist["name"], size=14, bold=True, cursor="hand2"
						).pack(fill="x", padx=12, pady=(8, 0))
			songs = playlist["song_count"]
			plain.label(card, f"{songs} song{'' if songs == 1 else 's'}", size=13,
						muted=True, cursor="hand2").pack(fill="x", padx=12, pady=(0, 8))

			# Clicks on a label don't reach the card, so bind every widget.
			# p=playlist freezes this card's playlist.
			card.configure(cursor="hand2")
			for widget in [card] + card.winfo_children():
				widget.bind("<Button-1>", lambda e, p=playlist: self.open(p["id"]))

	def new_playlist(self):
		name = self._ask_name("New playlist")
		if name is None:
			return
		self.service.create_playlist(name)
		self.refresh()

	def open(self, playlist_id):
		"""Switches to the detail view of one playlist."""
		self.open_playlist = playlist_id
		self.refresh()

	# --- Detail view ---

	def show_detail(self, playlist):
		songs = self.service.get_playlist_songs(playlist["id"])   # playlist order

		toolbar = ctk.CTkFrame(self.content, fg_color="transparent")
		toolbar.pack(fill="x", pady=(8, 0))

		ctk.CTkButton(toolbar, text="← Back", width=80, height=40, font=self.nav_font,
					  fg_color="transparent", border_width=1,
					  text_color=("gray10", "gray90"),
					  command=self.back).pack(side="left")
		ctk.CTkLabel(toolbar, text=playlist["name"], anchor="w",
					 font=ctk.CTkFont(family="Segoe UI Variable Text", size=16, weight="bold")
					 ).pack(side="left", padx=12)

		# Packed right to left, so Play ends up on the far right.
		# Play is disabled for an empty playlist: there's nothing to play.
		ctk.CTkButton(toolbar, text="▶ Play", width=90, height=40, font=self.nav_font,
					  state="normal" if songs else "disabled",
					  command=lambda: self.on_play_playlist(playlist["id"])).pack(side="right")
		ctk.CTkButton(toolbar, text="Rename", width=80, height=40, font=self.nav_font,
					  command=lambda: self.rename(playlist)).pack(side="right", padx=8)
		ctk.CTkButton(toolbar, text="Delete", width=80, height=40, font=self.nav_font,
					  fg_color=("#c0392b", "#a93226"), hover_color=("#a93226", "#922b21"),
					  command=lambda: self.delete(playlist)).pack(side="right")

		count = len(songs)
		ctk.CTkLabel(self.content, text=f"{count} song{'' if count == 1 else 's'}",
					 text_color="gray", anchor="w").pack(fill="x", pady=8)

		list_frame = ctk.CTkScrollableFrame(self.content)
		list_frame.pack(fill="both", expand=True)

		if not songs:
			ctk.CTkLabel(list_frame, text="This playlist is empty. Right-click a song on\n"
						 "All Songs and choose Add to playlist.",
						 text_color="gray").pack(pady=16)
			return

		for song in songs:
			card = plain.card(list_frame)
			card.pack(fill="x", pady=4, padx=4)
			card.grid_columnconfigure(0, weight=1)   # text stretches, ✕ stays right

			title = plain.label(card, song["title"], size=14, wraplength=400, cursor="hand2")
			title.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 0))
			artist = plain.label(card, song["artist"], size=13, muted=True, cursor="hand2")
			artist.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

			ctk.CTkButton(card, text="✕", width=32, height=32, fg_color="transparent",
						  text_color=("gray35", "gray75"), hover_color=("gray78", "gray25"),
						  command=lambda s=song: self.remove_song(playlist["id"], s)
						  ).grid(row=0, column=1, rowspan=2, padx=8)

			# Clicking a song plays the playlist from that song. The ✕ button
			# isn't bound, so removing a song doesn't also play it.
			card.configure(cursor="hand2")
			for widget in (card, title, artist):
				widget.bind("<Button-1>",
							lambda e, s=song: self.on_play_playlist(playlist["id"], start=s))

	def back(self):
		self.open_playlist = None
		self.refresh()

	def rename(self, playlist):
		name = self._ask_name("Rename playlist", f"New name for \"{playlist['name']}\":")
		if name is None:
			return
		self.service.rename_playlist(playlist["id"], name)
		self.refresh()

	def delete(self, playlist):
		# Deleting can't be undone, so ask first. The songs stay in the library.
		if not messagebox.askyesno("Delete playlist",
								   f"Delete \"{playlist['name']}\"?\n\n"
								   "The songs stay in your library.", parent=self):
			return
		self.service.delete_playlist(playlist["id"])
		self.open_playlist = None
		self.refresh()

	def remove_song(self, playlist_id, song):
		self.service.remove_from_playlist(playlist_id, song["id"])
		self.refresh()

	# --- Helpers ---

	def _find_playlist(self, playlist_id):
		return next((p for p in self.service.get_playlists() if p["id"] == playlist_id), None)

	def _ask_name(self, title, text="Playlist name:"):
		"""Asks for a playlist name. Returns it stripped, or None if the user
		cancelled or left it blank."""
		name = ctk.CTkInputDialog(title=title, text=text).get_input()
		if name is None or not name.strip():
			return None
		return name.strip()
