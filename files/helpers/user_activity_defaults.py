import time

from sqlalchemy import event, text


_installed = False


def install_user_activity_defaults(engine, User):
	"""Initialize real activity timestamps and repair legacy zero values."""
	global _installed
	if _installed:
		return

	@event.listens_for(User, "before_insert", propagate=True)
	def _initialize_last_active(mapper, connection, target):
		created_utc = int(getattr(target, "created_utc", 0) or time.time())
		target.created_utc = created_utc
		if not int(getattr(target, "last_active", 0) or 0):
			target.last_active = created_utc

	# A signup is activity. Older accounts created before this fix may still have
	# last_active=0, which the browser date formatter renders as January 1970.
	with engine.begin() as connection:
		connection.execute(text("""
			UPDATE users
			SET last_active = created_utc
			WHERE COALESCE(last_active, 0) = 0
			  AND created_utc IS NOT NULL
			  AND created_utc > 0
		"""))

	_installed = True
