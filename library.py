
import sqlite3, os
from datetime import datetime
import mutagen
import re


class Library:
	def __init__(self, path):
		self.conn = sqlite3.connect(path)
		self.conn.row_factory = sqlite3.Row

		self.conn.execute("""
		CREATE TABLE IF NOT EXISTS songs (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			platform TEXT NOT NULL,
			source_id TEXT,
			title TEXT NOT NULL,
			artist TEXT NOT NULL,
			url TEXT NOT NULL DEFAULT '',
			filepath TEXT NOT NULL UNIQUE,
			downloaded_at TEXT NOT NULL,
			UNIQUE (platform, source_id)
		)""")
		self.conn.commit()

	def add(self, result, filepath, autocommit=True):
		"""Records a song. Saves it right away unless autocommit is False,
		in which case the caller must call self.conn.commit() later (sync
		does this, to save many songs with one commit).
		"""
		response = self.conn.execute("""
			INSERT INTO songs (platform, source_id, title, artist, url, filepath, downloaded_at) VALUES (?, ?, ?, ?, ?, ?, ?)
		""",(result["platform"], result["source_id"], result["title"], result["artist"], result["url"], filepath, datetime.now().isoformat(timespec="seconds")))

		if autocommit:
			self.conn.commit()

		return response.lastrowid
		


	def has(self, platform, source_id):
		row = self.conn.execute("""
			SELECT 1 FROM songs
			WHERE platform = ? AND source_id = ?
		""", (platform,source_id)).fetchone()
		return row is not None 

	def get_all_songs(self):
		rows = self.conn.execute("""
			SELECT * FROM SONGS
		""").fetchall()

		return [dict(row) for row in rows]

	def get_history(self, newest=True):
		
		order = "DESC" if newest else "ASC"
		rows = self.conn.execute(f"SELECT * FROM songs ORDER BY downloaded_at {order}").fetchall()

		return [dict(row) for row in rows]

	def get_download_history(self, newest=True):
			
			order = "DESC" if newest else "ASC"
			rows = self.conn.execute(f"SELECT * FROM songs WHERE platform != 'local' ORDER BY downloaded_at {order}").fetchall()
	
			return [dict(row) for row in rows]

	def get_metadata(self, filepath):
		try:
			audio = mutagen.File(f"{filepath}",easy=True)
			if audio is not None:
				
				# "or None" turns an empty tag ("") into None too.
				title = audio.get("title", [None])[0] or None
				artist = audio.get("artist", [None])[0] or None

				return title, artist
			else:
				return (None, None)
		except:
			return (None, None)
		

	def sync(self, folder):
		os.makedirs(folder, exist_ok=True)
		on_disk = {file for file in os.listdir(folder) if file.lower().endswith(".mp3")}

		rows = self.conn.execute("SELECT filepath FROM songs").fetchall()
		in_db = {(row['filepath']) for row in rows}

		new_files = on_disk-in_db
		missing_files = in_db-on_disk

		if missing_files:
			for file in missing_files:
				self.conn.execute("""
					DELETE FROM songs WHERE filepath = ?

				""",(file,))

		if new_files:
			for file in new_files:
				name = os.path.splitext(file)[0]
				url = ''

				platform = 'local'
				# The name to show if the file has no title tag.
				clean_name = name

				match = re.search(r"\[([A-Za-z0-9_-]{11})\]$", name)
				source_id = None
				if match:
					platform = 'youtube'
					source_id = match.group(1)
					url = "https://www.youtube.com/watch?v=" + source_id
					# Everything before the "[", minus the space before it.
					clean_name = name[:match.start()].rstrip()

				title, artist = self.get_metadata(os.path.join(folder, file))

				title = title or clean_name
				artist = artist or "Unknown"
				result = {
					'platform' : platform,
					'source_id' : source_id,
					'title' : title,
					'artist' : artist,
					'url' : url
	  
				}
				try:
					self.add(result=result, filepath=file, autocommit=False)
				except sqlite3.IntegrityError:
					continue

		# One commit for every delete and add above: much faster than one
		# per song, and all-or-nothing if something fails halfway.
		if missing_files or new_files:
			self.conn.commit()

