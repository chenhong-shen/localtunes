"""
The base class every page in the app is built on.
"""

import customtkinter as ctk


class Page(ctk.CTkFrame):
	"""A page with a title at the top.

	Every page is a transparent frame, so the window's background shows
	through. The title is placed with pack, so everything else placed directly
	on a page must also use pack (never mix pack and grid in one container).

	Pages that don't have content yet (Playlists, Settings) are plain Pages.
	"""

	def __init__(self, parent, title, title_font):
		super().__init__(parent, fg_color="transparent")
		ctk.CTkLabel(self, text=title, font=title_font).pack(anchor="w")