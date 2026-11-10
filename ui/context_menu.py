"""
A right-click menu drawn with customtkinter, so it matches the rest of the app
(rounded corners, hover effects, light and dark mode) instead of looking like
a Windows system menu.
"""

import tkinter as tk
import customtkinter as ctk

from ui import plain


# Windows makes this exact color see-through. The window itself is always
# square; painting it this color and putting a rounded frame inside is what
# gives the menu rounded corners.
TRANSPARENT = "#010101"

ITEM_WIDTH = 200   # every item is at least this wide, so the menu doesn't look cramped


class ContextMenu:
	"""A popup menu that opens at (x, y) on screen.

	Add items with add_command / add_label / add_separator, then call show().
	It closes when an item is clicked, when anything else is clicked, or on
	Escape. Only one menu is open at a time: opening a new one closes the old.

	A plain tk.Toplevel is used for the window, not CTkToplevel: in dark mode
	CTkToplevel hides and re-shows itself to recolor its title bar, which
	makes a borderless popup flicker.
	"""

	_open = None   # the menu currently open, if any

	def __init__(self, parent, x, y):
		if ContextMenu._open is not None:
			ContextMenu._open.close()
		ContextMenu._open = self

		self.window = tk.Toplevel(parent, bg=TRANSPARENT)
		self.window.withdraw()                    # hidden until show() places it
		self.window.overrideredirect(True)        # no title bar or border
		self.window.attributes("-topmost", True)
		self.window.attributes("-transparentcolor", TRANSPARENT)

		self.frame = ctk.CTkFrame(self.window, corner_radius=8, border_width=1,
								  fg_color=("gray95", "gray17"),
								  border_color=("gray75", "gray30"),
								  bg_color=TRANSPARENT)
		self.frame.pack()
		# Room above the first item and below the last, inside the border.
		ctk.CTkFrame(self.frame, height=4, fg_color="transparent").pack()

		self._x, self._y = x, y
		self.window.bind("<Escape>", lambda e: self.close())
		self.window.bind("<FocusOut>", self._on_focus_out)

	# --- Items ---

	def add_command(self, label, command):
		"""A clickable item. The menu closes before `command()` runs, so the
		command can open a dialog without the menu staying on top of it."""
		ctk.CTkButton(self.frame, text=label, anchor="w", width=ITEM_WIDTH, height=30,
					  corner_radius=6, fg_color="transparent",
					  hover_color=("gray85", "gray25"), text_color=("gray10", "gray90"),
					  font=ctk.CTkFont(family="Segoe UI Variable Text", size=13),
					  command=lambda: self._run(command)
					  ).pack(fill="x", padx=4, pady=1)

	def add_label(self, text):
		"""A small gray heading that can't be clicked, like "Add to playlist"."""
		ctk.CTkLabel(self.frame, text=text, text_color="gray", anchor="w", height=22,
					 font=ctk.CTkFont(family="Segoe UI Variable Text", size=12)
					 ).pack(fill="x", padx=14, pady=(2, 0))

	def add_separator(self):
		# A plain tk.Frame: customtkinter draws nothing for a 1-pixel CTkFrame.
		# Its color is picked for the current mode, which is fine because the
		# menu is built fresh every time it opens.
		tk.Frame(self.frame, height=1, bg=plain.mode_color(("gray80", "gray30"))
				 ).pack(fill="x", padx=10, pady=4)

	# --- Showing and closing ---

	def show(self):
		"""Places the menu at (x, y), moved left or up if it would go off the
		screen, and shows it. Call after adding the items."""
		ctk.CTkFrame(self.frame, height=4, fg_color="transparent").pack()   # bottom room
		self.window.update_idletasks()
		width, height = self.window.winfo_reqwidth(), self.window.winfo_reqheight()
		x = max(0, min(self._x, self.window.winfo_screenwidth() - width))
		y = max(0, min(self._y, self.window.winfo_screenheight() - height))
		self.window.geometry(f"+{x}+{y}")
		self.window.deiconify()
		self.window.wait_visibility()   # grab_set fails on a window not shown yet

		# Clicks in the app: while the menu has the grab, every click in the
		# app's windows comes here (like a real tk.Menu does), so a click
		# outside the menu can close it.
		try:
			self.window.grab_set()
		except tk.TclError:
			pass   # another window has the grab; FocusOut still closes the menu
		self.window.bind("<ButtonPress>", self._on_click, add="+")

		# Clicks in other programs: they take the focus away, which closes it.
		self.window.after(10, self.window.focus_force)

	def close(self):
		if ContextMenu._open is self:
			ContextMenu._open = None
		if self.window.winfo_exists():
			self.window.grab_release()
			self.window.destroy()

	def _on_click(self, event):
		# Clicks on the items also arrive here (the window's bindings apply to
		# everything inside it), so only close for clicks outside the menu.
		w = self.window
		inside = (w.winfo_rootx() <= event.x_root < w.winfo_rootx() + w.winfo_width()
				  and w.winfo_rooty() <= event.y_root < w.winfo_rooty() + w.winfo_height())
		if not inside:
			self.close()

	def _run(self, command):
		self.close()
		command()

	def _on_focus_out(self, event):
		# FocusOut also fires when the focus moves between widgets inside the
		# menu, so wait a moment and only close if it really left the menu.
		self.window.after(50, self._close_if_unfocused)

	def _close_if_unfocused(self):
		if not self.window.winfo_exists():
			return
		try:
			focused = self.window.focus_get()
		except KeyError:   # focus is on a widget tkinter can't look up
			focused = None
		if focused is None or focused.winfo_toplevel() is not self.window:
			self.close()
