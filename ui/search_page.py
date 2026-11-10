"""
The Search page: searching YouTube, and downloading results.

Searching and downloading are slow, so they run on background threads
("workers"). Workers never touch widgets, because tkinter is not
thread-safe. Instead, a worker puts a message on self.events (a queue.Queue),
and poll_events, which runs on the main thread every 100 ms, applies it.

	click  ->  on_search / on_download      (main thread: start a worker)
	       ->  search_worker / download_worker   (background: slow work)
	       ->  self.events.put(...)          (hand the result back)
	       ->  poll_events()                 (main thread: update the UI)
"""

import queue
import threading
import customtkinter as ctk

from urllib.parse import urlparse

import settings

from ui import plain
from ui.page import Page


class SearchPage(Page):
	"""A search bar, a status line, and one card per result.

	Layout, top to bottom:
		[ platform v ] [ search entry ........ ] [ Search ]
		status line ("Searching...", "5 results", errors)
		scrollable results area (one card per result)

	The injected service handles catalog and library operations. This page
	keeps the background-worker and widget-update flow.
	"""

	def __init__(self, parent, title, title_font, nav_font, service, on_library_changed):
		super().__init__(parent, title, title_font)
		self.service = service
		self.on_library_changed = on_library_changed
		self.nav_font = nav_font
		self.plus_font = ctk.CTkFont(size=20, weight="bold")

		# (platform, source_id) of songs being downloaded right now. Together with the history,
		# this stops the same song from being downloaded twice: the history
		# covers finished downloads, this covers ones still in progress.
		self.downloading = set()

		# Messages from the workers to the main thread, as (kind, data).
		self.events = queue.Queue()

		# --- Search bar ---
		# A transparent frame that lines the three controls up in one row.
		bar = ctk.CTkFrame(self, fg_color="transparent")
		bar.pack(fill="x", pady=8)

		# Platform picker. To support another platform, add its name to
		# `values` and a branch in search_worker.
		self.platform_var = ctk.StringVar(value="YouTube")
		ctk.CTkOptionMenu(bar, values=["YouTube"], variable=self.platform_var,
						  width=120, height=40).pack(side="left")

		# expand=True makes the entry take whatever width is left over.
		self.search_entry = ctk.CTkEntry(bar, placeholder_text="Search for a song", height=40)
		self.search_entry.pack(side="left", fill="x", expand=True, padx=8)
		self.search_entry.bind("<Return>", lambda e: self.on_search())

		self.search_button = ctk.CTkButton(bar, text="Search", height=40, font=nav_font,
										   command=self.on_search)
		self.search_button.pack(side="left")

		# One line of gray text for feedback: progress, result counts, errors.
		self.status_label = ctk.CTkLabel(self, text="", text_color="gray", anchor="w")
		self.status_label.pack(fill="x")

		# Where result cards go.
		self.results_frame = ctk.CTkScrollableFrame(self)
		self.results_frame.pack(fill="both", expand=True)

		# Start applying worker messages. poll_events re-schedules itself.
		self.after(100, self.poll_events)

	# simple is youtube function
	def is_youtube_url(self, value):
		parsed = urlparse(value)
		host = (parsed.hostname or "").lower()

		return (
			parsed.scheme in {"http", "https"}
			and host in {
				"youtube.com",
				"www.youtube.com",
				"m.youtube.com",
				"music.youtube.com",
				"youtu.be",
			}
		)

	# ------------------------------------------------------------------
	# Searching
	# ------------------------------------------------------------------

	def on_search(self):
		"""Starts a search for the text in the search box. MAIN THREAD."""
		query = self.search_entry.get().strip()
		if not query:
			return

		if self.is_youtube_url(query):
				# if the searched query is a url
				platform = 'youtube'

				self.search_button.configure(state="disabled", text = "Downloading...")
				self.status_label.configure(text="Downloading from URL...")

				threading.Thread(target=self.url_download, args =(query,platform),daemon=True).start()
		else:
			platform = self.platform_var.get()

			# Disabled until the result (or an error) arrives, so only one
			# search runs at a time.
			self.search_button.configure(state="disabled", text="Searching...")
			self.status_label.configure(text=f"Searching {platform}...")

			threading.Thread(target=self.search_worker, args=(query, platform), daemon=True).start()

	def search_worker(self, query, platform):
		"""Runs the search. BACKGROUND THREAD: never touch widgets here.

		Sends exactly one message:
			("search_results", list of result dicts)   on success
			("search_error", error message string)     on any failure
		"""
		query = str(query)
		try:
			if platform == "YouTube":
				results = self.service.search(query=query, platform=platform, max_results=settings.load()["max_results"])
				
			else:
				raise ValueError(f"Unsupported platform: {platform}")
			self.events.put(("search_results", results))
		except Exception as e:
			# Catch everything: an uncaught exception in a thread would
			# vanish silently, and the Search button would stay disabled.
			self.events.put(("search_error", str(e)))

	def show_results(self, results):
		"""Replaces the result cards with one card per result. MAIN THREAD.

		Card layout:
			| Title (bold, wraps if long)                     | ( + ) |
			| Channel (gray)                                  |       |

		The button shows ✓ and is disabled for songs already in the history.
		"""
		# Hide the results area while rebuilding it, so it's redrawn once at
		# the end instead of after every card (which makes cards pop in one
		# at a time). It's re-packed with the same options as in __init__.
		self.results_frame.pack_forget()

		for widget in self.results_frame.winfo_children():
			widget.destroy()

		if not results:
			ctk.CTkLabel(self.results_frame, text="No results found", text_color="gray").pack(pady=16)
			self.results_frame.pack(fill="both", expand=True)
			return


		

		for result in results:
			# The card is packed into results_frame, but the widgets inside
			# the card use grid, so the + button can sit beside both lines.
			# Plain labels on a card-colored frame scroll without flickering
			# (see ui/plain.py).
			card = plain.card(self.results_frame)
			card.pack(fill="x", pady=4, padx=4)
			card.grid_columnconfigure(0, weight=1)

			plain.label(card, result["title"], size=14, wraplength=400
						).grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 0))
			plain.label(card, result["artist"], size=13, muted=True
						).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

			btn = ctk.CTkButton(card, text="+", width=36, height=36, corner_radius=18,
								font=self.plus_font)
			# Set after creating the button, because the lambda needs `btn`.
			# r=result and b=btn freeze this card's values.
			btn.configure(command=lambda r=result, b=btn: self.on_download(r, b))
			btn.grid(row=0, column=1, rowspan=2, padx=12)

			if self.service.has_song(result["platform"], result["source_id"]):
				btn.configure(state="disabled", text="✓")

		self.results_frame.pack(fill="both", expand=True)

	# ------------------------------------------------------------------
	# Downloading
	# ------------------------------------------------------------------

	def on_download(self, result, button):
		"""Starts downloading one result. MAIN THREAD.

		Does nothing (except update the status line) if the song is already
		downloaded or already downloading.
		"""
		# (platform, source_id) identifies the song both in the library and
		# in self.downloading.
		key = (result["platform"], result["source_id"])

		if self.service.has_song(*key):
			self.status_label.configure(text=f"Already downloaded: {result['title']}")
			button.configure(state="disabled", text="✓")
			return

		if key in self.downloading:
			self.status_label.configure(text=f"Already downloading: {result['title']}")
			return

		self.downloading.add(key)

		# "…" shows it's working; disabled stops a double-click.
		button.configure(state="disabled", text="…")
		self.status_label.configure(text=f"Downloading: {result['title']}")
		threading.Thread(target=self.download_worker, args=(result, button), daemon=True).start()

	def download_worker(self, result, button):
		"""Downloads the audio. BACKGROUND THREAD: never touch widgets here.

		`button` is only passed through the queue so poll_events can update it.

		Sends exactly one message:
			("download_done", (result, button, filepath))   on success
			("download_error", (result, button, message))   on any failure
		"""
		try:
			filepath = self.service.download(result)
		except Exception as e:
			self.events.put(("download_error", (result, button, str(e))))
			return

		self.events.put(("download_done", (result, button, filepath)))

	def url_download(self, url, platform):
		try:
			result = self.service.get_url_metadata(url,platform)
			
		except Exception as e:
			self.events.put(("url_metadata_error", (url, str(e))))
			return

		self.events.put(("url_metadata_resolved", result))


	def url_download_worker(self, result):
		try:
			filepath = self.service.download(result)
		except Exception as error:
			self.events.put(("url_download_error",(result,str(error))))
			return

		self.events.put(("url_download_done",(result,filepath)))


				



	# ------------------------------------------------------------------
	# Applying worker messages (main thread)
	# ------------------------------------------------------------------

	def poll_events(self):
		"""Applies every waiting worker message, then checks again in 100 ms.

		MAIN THREAD: the only place worker results reach the UI.
		"""
		while not self.events.empty():
			kind, data = self.events.get()

			if kind == "search_results":
				self.show_results(data)
				self.status_label.configure(text=f"{len(data)} results")
				self.search_button.configure(state="normal", text="Search")

			elif kind == "search_error":
				self.status_label.configure(text=f"Search failed: {data}")
				self.search_button.configure(state="normal", text="Search")

			elif kind == "download_done":
				result, button, filepath = data
				self.downloading.discard((result["platform"], result["source_id"]))

				# SQLite is only touched here, on the thread that created it.
				try:
					self.service.record_download(result, filepath)
				except Exception as err:
					self.status_label.configure(text=f"Could not save {result['title']}: {err}")
					if button.winfo_exists():
						button.configure(state="normal", text="+")
					continue

				self.on_library_changed()

				self.status_label.configure(text=f"Downloaded: {result['title']}")
				# A new search may have destroyed this card meanwhile.
				if button.winfo_exists():
					button.configure(text="✓")

			
				

			elif kind == "download_error":
				result, button, err = data
				self.downloading.discard((result["platform"], result["source_id"]))   # free it up for a retry
				self.status_label.configure(text=f"Download failed: {result['title']} ({err})")
				if button.winfo_exists():
					button.configure(state="normal", text="+")

			elif kind == "url_download_done":
				result, filepath = data
				self.downloading.discard((result["platform"], result["source_id"]))

				# SQLite is only touched here, on the thread that created it.
				try:
					self.service.record_download(result, filepath)
				except Exception as err:
					self.status_label.configure(text=f"Could not save {result['title']}: {err}")
					self.search_button.configure(state="normal", text = "Search")
					continue

				self.on_library_changed()

				self.status_label.configure(text=f"Downloaded: {result['title']}")
				self.search_button.configure(state="normal", text = "Search")

			elif kind == "url_metadata_resolved":
				result = data
				key = (result['platform'],result['source_id'])
				if self.service.has_song(*key):
					self.status_label.configure(text=f"Already downloaded: {result['title']}")
					self.search_button.configure(state="normal", text = "Search")
				elif key in self.downloading:
					self.status_label.configure(text=f"Already downloading: {result['title']}")
					self.search_button.configure(state="normal", text = "Search")
				else:
					self.downloading.add(key)
					threading.Thread(target=self.url_download_worker,args=(result,),daemon=True).start()
					
					
			elif kind == 'url_metadata_error':
				url, err = data
				self.status_label.configure(text=f"Metadata failed: {url} ({err})")
				self.search_button.configure(state="normal", text = "Search")

			elif kind == 'url_download_error':
				result, err = data

				self.downloading.discard((result["platform"],result["source_id"]))

				self.status_label.configure(text=f"Download failed: {result['title']} ({err})")
				self.search_button.configure(state="normal", text = "Search")
				


		self.after(100, self.poll_events)
