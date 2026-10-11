# ui/plain.py API

Version 1.0.0

Small Tkinter helpers for drawing labels inside scrolling cards. Plain Tk
labels scroll with less flicker than customtkinter labels, but their colors
are selected when they are created and do not follow later appearance-mode
changes.

## Module constants

| Constant | Meaning |
|---|---|
| `CARD_COLOR` | Light/dark background pair for cards. |
| `TEXT_COLOR` | Light/dark foreground pair for normal labels. |
| `MUTED_COLOR` | Light/dark foreground pair for muted labels. |
| `FONT_FAMILY` | Font family used by plain labels (`"Segoe UI Variable Text"`). |

## Module functions

### `mode_color(color)`

If `color` is a list or tuple, returns its dark-mode value when
`customtkinter.get_appearance_mode()` is `"Dark"`, otherwise its light-mode
value. Other values are returned unchanged. An empty pair raises
`IndexError`.

### `card(parent, corner_radius=0)`

Creates and returns a `customtkinter.CTkFrame` with `CARD_COLOR` as its
foreground color.

| Argument | Meaning |
|---|---|
| `parent` | The widget that owns the frame. |
| `corner_radius` (`int` or `float`) | Frame corner radius. Defaults to `0`. |
| **Returns** | `CTkFrame`. |

### `display_scaling(widget)`

Returns customtkinter's widget scaling for `widget`. If reading it raises an
exception, returns `1.0`.

| Argument | Meaning |
|---|---|
| `widget` | Widget whose display scaling should be read. |
| **Returns** | `float`. |

### `label(parent, text, size=14, bold=False, muted=False, wraplength=0, cursor="")`

Creates and returns a plain `tkinter.Label` whose foreground and background
match the selected card colors. `size` and `wraplength` are multiplied by
the parent's display scaling. The label uses left alignment and wrapping.

| Argument | Meaning |
|---|---|
| `parent` | The widget that owns the label, normally a frame from `card()`. |
| `text` | Label text. |
| `size` (`int` or `float`) | Font size in pixels; defaults to `14`. |
| `bold` (`bool`) | Whether to use a bold font; defaults to `False`. |
| `muted` (`bool`) | Whether to use `MUTED_COLOR`; defaults to `False`. |
| `wraplength` (`int` or `float`) | Wrapping width in pixels; `0` disables wrapping. |
| `cursor` (`str`) | Tk cursor name; defaults to the system default. |
| **Returns** | `tkinter.Label`. |
