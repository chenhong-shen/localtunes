"""
Plain tkinter labels for use inside scrolling areas.

customtkinter draws every widget on its own canvas, and a scrollable frame
has to repaint every one of them as it scrolls, which flickers. Plain
tkinter labels are drawn natively by Windows and scroll smoothly. They don't
follow customtkinter's theme, though, so their colors are set here, and
their background must match the card they sit on.
"""

import tkinter as tk
import customtkinter as ctk


# (light mode, dark mode) pairs, like customtkinter's own colors.
CARD_COLOR = ("gray86", "gray17")
TEXT_COLOR = ("gray10", "gray90")
MUTED_COLOR = ("gray40", "gray55")

FONT_FAMILY = "Segoe UI Variable Text"


def mode_color(color):
	"""Turns a (light, dark) color pair into the one for the current mode."""
	if isinstance(color, (list, tuple)):
		return color[1] if ctk.get_appearance_mode() == "Dark" else color[0]
	return color


def card(parent, corner_radius=0):
	"""A customtkinter frame in the card color, for placing plain labels on."""
	return ctk.CTkFrame(parent, corner_radius=corner_radius, fg_color=CARD_COLOR)


def display_scaling(widget):
	"""How much customtkinter is enlarging widgets for Windows display
	scaling: 1.0 at 100%, 1.5 at 150%, and so on.

	Plain tk sizes in pixels aren't enlarged automatically, so they're
	multiplied by this to match the customtkinter widgets around them. If
	customtkinter's scaling can't be read, assumes 100%.
	"""
	try:
		return ctk.ScalingTracker.get_widget_scaling(widget)
	except Exception:
		return 1.0


def label(parent, text, size=14, bold=False, muted=False, wraplength=0, cursor=""):
	"""A plain tk label whose background matches a frame made with card().

	`size` is in pixels, like customtkinter fonts. In plain tkinter a
	negative font size means pixels (a positive one means points), which is
	why it's negated below. Both `size` and `wraplength` are scaled to match
	the display scaling, the same way customtkinter scales its own widgets.

	The colors are picked for the current light/dark mode when the label is
	created; they don't change if the mode changes later.
	"""
	scale = display_scaling(parent)
	return tk.Label(
		parent,
		text=text,
		font=(FONT_FAMILY, -round(size * scale), "bold" if bold else "normal"),
		fg=mode_color(MUTED_COLOR if muted else TEXT_COLOR),
		bg=mode_color(CARD_COLOR),
		anchor="w",
		justify="left",
		wraplength=round(wraplength * scale),
		cursor=cursor,
	)