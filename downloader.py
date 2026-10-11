import yt_dlp
import os

class Download:
	def __init__(self, url, folder, ffmpeg_folder):

		if not isinstance(url, str):
			raise TypeError("url must be a string.")

		if not url:
			raise ValueError("Must provide a valid url.")


		self.url = url
		self.folder = folder
		self.ffmpeg_folder = ffmpeg_folder

	def download_youtube(self):
		ydl_options = {
			'format': 'bestaudio/best',
			'outtmpl': os.path.join(self.folder, '%(title)s [%(id)s].%(ext)s'),
			'ffmpeg_location': self.ffmpeg_folder,
			# Run in order: first convert to mp3, then write the video's
			# title, artist, etc. into the mp3's tags.
			'postprocessors': [
				{
					'key': 'FFmpegExtractAudio',
					'preferredcodec': 'mp3',
					'preferredquality': '192',
				},
				{
					'key': 'FFmpegMetadata',
					'add_metadata': True,
				},
			],
		}

		with yt_dlp.YoutubeDL(ydl_options) as ydl:
			info = ydl.extract_info(self.url, download=True)
			path = info['requested_downloads'][0]['filepath']
			return os.path.splitext(path)[0] + ".mp3"
		

		