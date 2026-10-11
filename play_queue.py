import random

class PlayQueue:
	def __init__(self, song_list, shuffle_enabled):

		self.song_list = song_list.copy()
		self.song_index = -1
		self.shuffle_enabled = shuffle_enabled
		


	def create_queue(self):
		if self.shuffle_enabled:
			random.shuffle(self.song_list)
		self.song_index = -1
		return self.song_list

	def next_song(self):
		if self.song_index >= len(self.song_list)-1:
			self.create_queue()
		
		self.song_index += 1

		song = self.song_list[self.song_index]
		
		return song

	def current_song(self):
		if not self.song_list:
			return None
		return self.song_list[self.song_index]

	
