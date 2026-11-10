import json
from paths import SETTINGS_FILE

DEFAULTS = {
	"appearance" : "System",
	"use_custom_background" : False,
	"volume" : 1,
	"max_results" : 10
}

def load():
	"""Returns the saved settings, using the defaults for anything missing."""
	try:
		with open(SETTINGS_FILE, encoding="utf-8") as f:
			return {**DEFAULTS, **json.load(f)}
	except (FileNotFoundError, json.JSONDecodeError):
		return dict(DEFAULTS)

def save(settings):
	with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
		json.dump(settings, f, indent=4)