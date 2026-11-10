"""The Settings page: theme, volume and search options."""

import customtkinter as ctk
import settings
from ui.page import Page


class SettingsPage(Page):
	"""One row per setting: a label on the left, a control on the right."""

	def __init__(self, parent, title, title_font, nav_font, service,
				 player, on_appearance_changed):
		super().__init__(parent, title, title_font)
		self.service = service
		self.player = player
		self.on_appearance_changed = on_appearance_changed
		self.settings = settings.load()

		# --- Theme ---
		row = self._row("Theme")
		self.appearance = ctk.CTkSegmentedButton(
			row, values=["Light", "Dark", "System"], command=self.set_appearance)
		self.appearance.pack(side="right")

		# --- Volume ---
		row = self._row("Volume")
		self.volume = ctk.CTkSlider(row, from_=0, to=1, command=self.set_volume)
		self.volume.pack(side="right")

		# --- Search results ---
		row = self._row("Search results")
		self.max_results = ctk.CTkOptionMenu(
			row, values=[str(n) for n in range(5, 21, 5)], command=self.set_max_results)
		self.max_results.pack(side="right")

		self.refresh()

	def _row(self, text):
		"""A transparent row with a label on the left. Returns the row."""
		row = ctk.CTkFrame(self, fg_color="transparent")
		row.pack(fill="x", pady=8)
		ctk.CTkLabel(row, text=text, anchor="w").pack(side="left")
		return row

	def refresh(self):
		"""Makes the controls show the saved settings. MAIN THREAD."""
		self.appearance.set(self.settings["appearance"])
		self.volume.set(self.settings["volume"])
		self.max_results.set(str(self.settings["max_results"]))

	def set_appearance(self, mode):
		self.settings["appearance"] = mode
		settings.save(self.settings)
		ctk.set_appearance_mode(mode)
		self.on_appearance_changed()

	def set_volume(self, value):
		self.settings["volume"] = value
		self.player.set_volume(value)
		settings.save(self.settings)

	def set_max_results(self, value):
		self.settings["max_results"] = int(value)
		settings.save(self.settings)