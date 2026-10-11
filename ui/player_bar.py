"""
The playback bar along the bottom of the window.
"""

import os
import customtkinter as ctk

from formatting import format_time
from paths import song_path
from thumbnails import load_thumbnail
from play_queue import PlayQueue


class PlayerBar(ctk.CTkFrame):
	"""Shows what's playing and controls playback.

	Layout, left to right:
		[ art ] [ title / artist ]  ( ▶ )  [ ========o-------- ]  0:00 / 0:00

	`player` is the app's Player. The bar keeps itself up to date by
	checking the player every 500 ms.
	"""

	def __init__(self, parent, player, on_missing, service):
		super().__init__(parent, height=72, corner_radius=0)
		self.player = player
		self.grid_columnconfigure(3, weight=1)   # the slider stretches
		self.on_missing = on_missing

		# --- Now playing: thumbnail ---
		# Starts as a gray placeholder with a music note. play_song swaps in
		# the real thumbnail.
		self.art = ctk.CTkLabel(self, text="♪", width=64, height=36,
								corner_radius=4, fg_color=("gray80", "gray25"),
								text_color="gray", font=ctk.CTkFont(size=18))
		self.art.grid(row=0, column=0, padx=(16, 0), pady=12)

		# --- Now playing: title and artist ---
		# A fixed-width frame, so long titles can't push the controls around.
		info = ctk.CTkFrame(self, fg_color="transparent", width=220, height=48)
		info.grid(row=0, column=1, padx=(10, 16), pady=12, sticky="w")
		info.grid_propagate(False)   # keep the fixed size instead of shrinking to fit

		self.title_label = ctk.CTkLabel(info, text="Nothing playing", anchor="w",
										font=ctk.CTkFont(family="Segoe UI Variable Text", size=13, weight="bold"))
		self.title_label.grid(row=0, column=0, sticky="w")

		self.artist_label = ctk.CTkLabel(info, text="", text_color="gray", anchor="w")
		self.artist_label.grid(row=1, column=0, sticky="w")

		# --- Play / pause and shuffle ---
		# Keep the controls in their own frame so the buttons don't overlap.
		controls = ctk.CTkFrame(self, fg_color="transparent")
		controls.grid(row=0, column=2, padx=4)

		self.shuffle_enabled = False
		self.shuffle_button = ctk.CTkButton(
			controls, text="⇄", width=32, height=36,
			corner_radius=18,
			font=ctk.CTkFont(family="Segoe UI Symbol", size=16),
			fg_color="transparent",
			text_color=("gray35", "gray75"),
			hover_color=("gray85", "gray25"),
			command=self.toggle_shuffle
		)
		self.shuffle_button.grid(row=0, column=0, padx=(0, 4))

		self.service = service

		# Round: corner_radius is half the size.
		# A widget's parent can't be changed after it's created, so the
		# button is created directly inside `controls`.
		self.play_button = ctk.CTkButton(controls, text="▶", width=44, height=44,
										corner_radius=22, font=ctk.CTkFont(family="Segoe UI Symbol", size=16),
										command=self.toggle_play_pause)
		self.play_button.grid(row=0, column=1, padx=4)

		# --- Progress / seek ---
		# The slider runs from 0 to 1, as a fraction of the song. While it's
		# dragged, on_seek_drag previews the time; on release, it seeks.
		self.progress = ctk.CTkSlider(self, from_=0, to=1, command=self.on_seek_drag)
		self.progress.set(0)
		self.progress.grid(row=0, column=3, padx=8, sticky="ew")

		# True while the mouse button is held down on the slider, so refresh
		# doesn't move it (or the time) while you drag it.
		self.user_seeking = False
		self.progress.bind("<ButtonPress-1>", lambda e: setattr(self, "user_seeking", True))
		self.progress.bind("<ButtonRelease-1>", lambda e: self.on_seek_release())

		# The dot only shows while the mouse is over the bar, like Spotify:
		# otherwise it's the same color as the filled part, so it blends in.
		fill = self.progress.cget("progress_color")
		self.progress.configure(button_color=fill, button_hover_color="white")
		self.progress.bind("<Enter>", lambda e: self.progress.configure(button_color="white"))
		self.progress.bind("<Leave>", lambda e: self.progress.configure(button_color=fill))

		# --- Time ---
		self.time_label = ctk.CTkLabel(self, text="0:00 / 0:00", text_color="gray", width=90)
		self.time_label.grid(row=0, column=4, padx=(8, 16))

		self.PlayQueue = PlayQueue(song_list=self.service.get_all_songs(),shuffle_enabled=False)

		# Keep the bar up to date. refresh re-schedules itself.
		self.after(500, self.refresh)


	

	def play_song(self, song):
		"""Plays `song`, a library entry. Called when a song box is clicked.

		If the song's file is gone, stops playback, shows "File not found"
		with the song's title, and calls on_missing so the app can resync.
		"""
		path = song_path(song["filepath"])

		if not os.path.exists(path):
			self.player.stop()

			missing_title = song["title"]
			if len(missing_title) > 30:
				missing_title = missing_title[:29] + "…"

			self.title_label.configure(text="File not found")
			self.artist_label.configure(text=missing_title)
			# "" not None: see the note in the else-branch below.
			self.art.configure(image="", text="♪")
			self.play_button.configure(text="▶")

			self.on_missing()
			return

		self.player.load(path)
		self.player.play()
		self.PlayQueue.set_current(song)

		title = song["title"]
		if len(title) > 30:
			title = title[:29] + "…"

		artist = song["artist"]
		if len(artist) > 15:
			artist = artist[:15] + "…"

		self.title_label.configure(text=title)
		self.artist_label.configure(text=artist)

		picture = load_thumbnail(song["platform"], song["source_id"], size=(64, 36))
		if picture is not None:
			self.art.configure(image=picture, text="")
		else:
			# image="" and not None: with None, customtkinter forgets the old
			# picture but the label keeps showing it. Once Python deletes the
			# picture, the next configure fails with 'image "pyimageN" does
			# not exist'. "" clears it from the label properly.
			self.art.configure(image="", text="♪")

		self.play_button.configure(text="⏸")

	def toggle_play_pause(self):
		"""Pauses, resumes, or replays a finished song.

		Does nothing while stopped: the only stop is after a missing file,
		and the song still loaded then is the previous one.
		"""
		if not self.player.loaded or self.player.stopped:
			return

		if self.player.is_finished():
			self.player.play()
			self.play_button.configure(text="⏸")
		elif self.player.is_playing():
			self.player.pause()
			self.play_button.configure(text="▶")
		else:
			self.player.resume()
			self.play_button.configure(text="⏸")

	def refresh(self):
		"""Refreshes the bar. Runs every 500 ms on the main thread."""
		position = self.player.position()
		duration = self.player.duration()

		# While the user drags, on_seek_drag controls the time and slider.
		if not self.user_seeking:
			self.time_label.configure(text=f"{format_time(position)} / {format_time(duration)}")
			if duration > 0:   # nothing loaded: 0, which would divide by zero
				self.progress.set(position / duration)

		if self.player.is_finished():
			if self.shuffle_enabled:
				self.PlayQueue.set_songs(self.service.get_all_songs())
				next_song = self.PlayQueue.next_song()
				if next_song is not None:
					self.play_song(next_song)
				else:
					self.play_button.configure(text="▶")
			else:
				self.play_button.configure(text="▶")
			

		# Keep this as the last line: it schedules the next update.
		self.after(500, self.refresh)

	def on_seek_drag(self, value):
		"""While dragging: show the time you'd jump to, without seeking yet."""
		duration = self.player.duration()
		self.time_label.configure(text=f"{format_time(value * duration)} / {format_time(duration)}")

	def on_seek_release(self):
		"""Seeks to where the slider was released."""
		self.user_seeking = False
		# Stopped means the last click was a missing file; seeking would
		# restart the previous song.
		if not self.player.loaded or self.player.stopped:
			return
		self.player.seek(self.progress.get() * self.player.duration())

		if not self.player.paused:
			self.play_button.configure(text="⏸")

	def toggle_shuffle(self):
		"""Toggle the shuffle button's visual state."""
		self.shuffle_enabled = not self.shuffle_enabled
		self.PlayQueue.toggle_shuffle(current_song=self._current_library_song())

		if self.shuffle_enabled:
			# turn on shuffle
			self.shuffle_button.configure(
				fg_color=("gray80", "gray25"),
				text_color=("gray10", "white")
			)
		else:
			# turn off shuffle
			self.shuffle_button.configure(
				fg_color="transparent",
				text_color=("gray35", "gray75")
			)

	def _current_library_song(self):
		"""Return the library entry for the track currently loaded in Player."""
		path = self.player.get_current_song()
		if path is None:
			return None
		return next((song for song in self.service.get_all_songs()
					 if song_path(song["filepath"]) == path), None)

