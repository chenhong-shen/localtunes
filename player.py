import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
from mutagen.mp3 import MP3
from paths import song_path


class Player:
	def __init__(self):
		pygame.mixer.init()
		self.length = 0
		self.offset = 0
		self.loaded = False
		self.started = False
		self.paused = False
		self.stopped = False
		self.current_song = None
		# Remembered so load() can apply it again: pygame resets the music
		# volume to full whenever a new song is loaded.
		self.volume = 1.0

	

	def load(self, filepath):
		if not isinstance(filepath, str):
			raise TypeError("Invalid filepath, must be str")
		if not os.path.exists(filepath):
			raise FileNotFoundError("Could not find the file path")

		pygame.mixer.music.load(filepath)
		self.length = MP3(filepath).info.length
		self.loaded = True

		self.started = False
		self.paused = False
		self.stopped = False
		self.offset = 0
		self.current_song = (filepath)
		pygame.mixer.music.set_volume(self.volume)

	def get_current_song(self):
		return self.current_song

	def set_volume(self, value):
		"""Sets the volume, from 0.0 (silent) to 1.0 (full). Kept for every
		song loaded afterwards too."""
		self.volume = max(0.0, min(1.0, value))
		pygame.mixer.music.set_volume(self.volume)

	def play(self):
		if not self.loaded:
			raise RuntimeError("No song loaded")

		self.started = True
		self.paused = False
		self.stopped = False
		self.offset = 0
		pygame.mixer.music.play()

	def pause(self):
		self.paused = True
		pygame.mixer.music.pause()

	def resume(self):
		self.paused = False
		pygame.mixer.music.unpause()

	def stop(self):
		self.stopped = True
		self.paused = False
		pygame.mixer.music.stop()

	def seek(self, seconds):
		if not self.loaded:
			raise RuntimeError("No song loaded")

		seconds = max(0, min(seconds, self.length))
		was_paused = self.paused

		pygame.mixer.music.play(start=seconds)
		self.offset = seconds
		self.started = True
		self.stopped = False
		self.paused = False

		if was_paused:
			self.pause()

	def position(self):
		if not self.started or self.stopped:
			return 0

		elapsed = pygame.mixer.music.get_pos()
		if elapsed < 0:
			elapsed = 0

		return min(self.offset + elapsed / 1000, self.length)

	def duration(self):
		return self.length

	def is_playing(self):
		return (self.started and not self.paused and not self.stopped and pygame.mixer.music.get_busy())

	def is_finished(self):
		return (self.started and not self.paused and not self.stopped and not pygame.mixer.music.get_busy())