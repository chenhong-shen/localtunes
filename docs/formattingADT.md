# formatting.py API

Version 1.0.0

Turning numbers and dates into text for display.

`ui/formatting.py` re-exports this module for UI code; its behavior is the
same as the functions documented here.

## Module functions

### `format_time(seconds)`

Converts `seconds` with Python's `int()` and formats that value as minutes
and seconds. Fractional parts are truncated toward zero; values are not
explicitly checked for negativity.

| | |
|---|---|
| `seconds` | Any value accepted by `int()`. |
| **Returns** | `str`. The converted integer as `m:ss`, for example `83.4` gives `'1:23'`. Minutes are not limited to 59: `3725` gives `'62:05'`. |
| **Raises** | Errors from `int()` for values it cannot convert, including `TypeError`, `ValueError`, or `OverflowError`. |

---

### `format_date(iso_text)`

Formats a stored date for display.

| | |
|---|---|
| `iso_text` (`str`) | A date and time in ISO format, as stored in a library entry, for example `'2026-10-08T22:35:00'`. |
| **Returns** | `str`. The date in a short readable form, for example `'Oct 8, 10:35 PM'`. If `iso_text` is not a valid ISO date, it is returned unchanged (as a `str`). |
| **Raises** | Nothing. |

Uses Windows-specific date formatting.
