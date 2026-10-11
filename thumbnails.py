"""
Saving and loading song thumbnails.
"""

import os
import requests
import customtkinter as ctk
from PIL import Image

from paths import THUMBNAIL_FOLDER, thumbnail_path


def save_thumbnail(platform, source_id):
	"""Downloads a video's thumbnail from YouTube and saves it as a .jpg.

	YouTube serves thumbnails at a fixed address built from the video ID.
	'mqdefault' is the 320x180 size, which is already 16:9, so it has no
	black bars. Raises requests.RequestException if the download fails.
	"""
	url = f"https://i.ytimg.com/vi/{source_id}/mqdefault.jpg"
	response = requests.get(url, timeout=10)
	response.raise_for_status()   # turn a 404 or similar into an exception

	os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)
	# "wb" = write bytes, since an image is binary data, not text.
	with open(thumbnail_path(platform, source_id), "wb") as f:
		f.write(response.content)


def load_thumbnail(platform, source_id, size):
	"""Returns the saved thumbnail as a CTkImage, or None if there isn't one.

	Returns None (instead of raising) when the file is missing or isn't a
	readable image, so one bad file can't break the UI.
	"""
	if source_id is None:
		return None
	
	path = thumbnail_path(platform, source_id)

	if not os.path.exists(path):
		return None
	try:
		picture = Image.open(path)
		picture.load()   # read it now, so a broken file fails here, inside the try
	except Exception:
		return None
	# The same image is used for light and dark mode.
	return ctk.CTkImage(light_image=picture, dark_image=picture, size=size)