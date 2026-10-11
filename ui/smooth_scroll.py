import customtkinter as ctk


class SmoothScrollableFrame(ctk.CTkScrollableFrame):
	"""A scrollable frame that responds properly to touchpads.

	CTkScrollableFrame throws away small wheel deltas, which is what
	touchpads send. This scrolls by pixels instead, so nothing is lost.
	"""

	SPEED = 0.5   # pixels per wheel-delta unit; a mouse notch (120) = 60 px

	def _is_inside(self, widget, canvas):
		"""True if `widget` is the canvas or one of its descendants."""
		while widget is not None and not isinstance(widget, str):
			if widget is canvas:
				return True
			widget = getattr(widget, "master", None)
		return False

	def _mouse_wheel_all(self, event):
		canvas = self._parent_canvas

		# Only react when the cursor is over this frame's contents.
		if not self._is_inside(event.widget, canvas):
			return

		if canvas.yview() == (0.0, 1.0):   # everything fits, nothing to scroll
			return

		bbox = canvas.bbox("all")
		if not bbox:
			return
		content_height = bbox[3] - bbox[1]
		if content_height <= 0:
			return

		top = canvas.yview()[0]
		canvas.yview_moveto(top - (event.delta * self.SPEED) / content_height)