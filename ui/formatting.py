"""
Turning numbers and dates into text for display.
"""

from datetime import datetime


def format_time(seconds):
	"""Turns a number of seconds into "m:ss", like 83.4 -> "1:23"."""
	minutes, secs = divmod(int(seconds), 60)
	return f"{minutes}:{secs:02d}"


def format_date(iso_text):
	"""Turns '2026-10-08T22:35:00' into 'Oct 8, 10:35 PM'.

	If the text isn't a valid date, it is returned unchanged, so one bad
	entry in the library can't crash the page.
	"""
	try:
		when = datetime.fromisoformat(iso_text)
	except (TypeError, ValueError):
		return str(iso_text)
	# %#d and %#I drop the leading zero on Windows ("8", not "08").
	# (On macOS or Linux these would be %-d and %-I instead.)
	return when.strftime("%b %#d, %#I:%M %p")