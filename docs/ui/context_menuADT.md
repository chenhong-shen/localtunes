# ui/context_menu.py API

Version 1.0.0

A right-click menu drawn with customtkinter, so it matches the app (rounded
corners, hover effects, light and dark mode) instead of looking like a
Windows system menu. Used by `LibraryPage` for the song menu.

## class `ContextMenu`

A borderless `tk.Toplevel` holding a rounded `CTkFrame`. The rounded corners
come from Windows' `-transparentcolor`, so they only work on Windows. A plain
`tk.Toplevel` is used, not `CTkToplevel`: in dark mode `CTkToplevel` hides
and re-shows itself to recolor its title bar, which makes a popup flicker.

Only one menu is open at a time; opening one closes the previous one. The
menu is built fresh each time it opens, so it always matches the current
light/dark mode. Every method runs on the **main thread**.

---

### `ContextMenu(parent, x, y)`

Creates a hidden menu that will open at screen position `(x, y)`, for
example `event.x_root, event.y_root` from a click.

### `menu.add_command(label, command)`

A clickable item. Clicking it closes the menu, then calls `command()`, so
the command can open a dialog.

### `menu.add_label(text)`

A small gray heading that can't be clicked.

### `menu.add_separator()`

A thin line between groups of items.

### `menu.show()`

Shows the menu after the items are added, moved left or up if it would go
off the screen.

### `menu.close()`

Closes the menu. Does nothing if it is already closed.

## When it closes

| What happens | How it's noticed |
|---|---|
| An item is clicked | `add_command` closes it before running the command. |
| A click anywhere else in the app | The menu holds the app's grab while open (like `tk.Menu`), so every click comes to it; clicks outside it close it. |
| A click in another program | The menu loses the focus. |
| Escape | Bound on the menu window. |
| Another menu opens | Only one is open at a time. |

```python
menu = ContextMenu(self, event.x_root, event.y_root)
menu.add_command("▶   Play", lambda: self.on_play(song))
menu.add_separator()
menu.add_label("Add to playlist")
menu.add_command("      Gym Mix", lambda: ...)
menu.show()
```
