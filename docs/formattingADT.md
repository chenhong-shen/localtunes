# formatting.py API

Version 1.0.0

Turning numbers and dates into text for display.

## Module functions

### `format_time(seconds)`

Formats a length of time as minutes and seconds.

| | |
|---|---|
| `seconds` (`int` or `float`) | A length of time, in seconds. Not negative. |
| **Returns** | `str`. The time as `m:ss`, for example `83.4` gives `'1:23'`. Parts of a second are dropped, not rounded. Minutes are not limited to 59: `3725` gives `'62:05'`. |
| **Raises** | `TypeError` or `ValueError` if `seconds` is not a number. |

---

### `format_date(iso_text)`

Formats a stored date for display.

| | |
|---|---|
| `iso_text` (`str`) | A date and time in ISO format, as stored in a library entry, for example `'2026-10-08T22:35:00'`. |
| **Returns** | `str`. The date in a short readable form, for example `'Oct 8, 10:35 PM'`. If `iso_text` is not a valid ISO date, it is returned unchanged (as a `str`). |
| **Raises** | Nothing. |

Uses Windows-specific date formatting.
