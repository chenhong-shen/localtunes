# ui/page.py API

Version 1.0.0

The base class every page in the app is built on.

## class `Page`

A page with a title at the top. Subclass of `customtkinter.CTkFrame`.

Every page is transparent, so the window's background shows through. Pages
that have no content yet (Playlists) are plain `Page`s.

**Rule for subclasses:** the title is placed with `pack`, so every widget
placed directly on a page must also use `pack`. Using `grid` directly on a
page raises a `TclError`. Widgets inside a frame on the page may use either.

---

### `Page(parent, title, title_font)`

Constructor. Builds an empty page showing only its title.

| | |
|---|---|
| `parent` | The widget the page belongs in. |
| `title` (`str`) | The text shown at the top of the page. |
| `title_font` (`CTkFont`) | The font for the title. |
| **Returns** | `Page`. |
