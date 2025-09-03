"""leaves app package"""

# Import signal handlers so they're registered when the app loads
try:
	from . import signals  # noqa: F401
except Exception:
	# If signals can't be imported at import time (tests/migrations), swallow error
	pass
