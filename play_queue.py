import random


class PlayQueue:
	"""Tracks playback order without changing the library's song list."""

	def __init__(self, song_list, shuffle_enabled=False):
		self.song_list = list(song_list)
		self.shuffle_enabled = shuffle_enabled
		self.queue = []
		self.song_index = -1
		self.create_queue()

	def _find_song(self, songs, song):
		if song is None:
			return -1
		filepath = song.get("filepath")
		return next((i for i, item in enumerate(songs)
					 if item.get("filepath") == filepath), -1)

	def create_queue(self, current_song=None):
		"""Rebuild the order, keeping the current song at its current position."""
		if current_song is None:
			current_song = self.current_song()

		self.queue = self.song_list.copy()
		current_index = self._find_song(self.queue, current_song)
		if self.shuffle_enabled:
			if current_index >= 0:
				current = self.queue.pop(current_index)
				random.shuffle(self.queue)
				self.queue.insert(0, current)
				self.song_index = 0
			else:
				random.shuffle(self.queue)
				self.song_index = -1
		else:
			self.song_index = current_index
		return self.queue

	def set_songs(self, song_list):
		"""Refresh the library snapshot while retaining the active song."""
		current = self.current_song()
		self.song_list = list(song_list)
		self.create_queue(current)

	def set_current(self, song):
		"""Align the queue with a song selected directly from the library."""
		if self.shuffle_enabled:
			self.create_queue(song)
			return
		index = self._find_song(self.queue, song)
		if index < 0:
			self.song_list.append(song)
			self.create_queue(song)
		else:
			self.song_index = index

	def toggle_shuffle(self, current_song=None):
		self.shuffle_enabled = not self.shuffle_enabled
		self.create_queue(current_song)
		return self.shuffle_enabled

	def next_song(self):
		if not self.queue:
			return None

		if self.song_index < 0:
			self.song_index = 0
		elif self.song_index < len(self.queue) - 1:
			self.song_index += 1
		elif self.shuffle_enabled:
			# Start a fresh shuffled round after every song has been played.
			previous = self.current_song()
			self.create_queue(previous)
			if len(self.queue) > 1:
				self.song_index = 1
			else:
				self.song_index = 0
		else:
			self.song_index = 0

		return self.queue[self.song_index]

	def current_song(self):
		if 0 <= self.song_index < len(self.queue):
			return self.queue[self.song_index]
		return None
