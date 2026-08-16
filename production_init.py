import os
import time
from pathlib import Path

import psycopg2


ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "schema.sql"
SEED = ROOT / "seed-db.sql"
PAYPAL_SCHEMA = ROOT / "paypal_schema.sql"


def database_url():
	value = os.environ["DATABASE_URL"].strip()
	if value.startswith("postgres://"):
		value = "postgresql://" + value[len("postgres://"):]
	return value


def connect_with_retry():
	last_error = None
	for _ in range(60):
		try:
			return psycopg2.connect(database_url())
		except psycopg2.OperationalError as error:
			last_error = error
			time.sleep(2)
	raise RuntimeError("PostgreSQL was not ready after 120 seconds") from last_error


def ensure_paypal_schema(cursor):
	cursor.execute(PAYPAL_SCHEMA.read_text(encoding="utf-8"))


def ensure_award_effect_schema(cursor):
	"""Keep per-award effect metadata out of the legacy VARCHAR(20) kind column."""
	cursor.execute(
		"""
		ALTER TABLE public.award_relationships
		ADD COLUMN IF NOT EXISTS emoji_name VARCHAR(80)
		"""
	)
	# A short-lived implementation encoded Emoji metadata as `wholesome:name`.
	# Migrate any rows that fit the old kind column, then restore the stable key.
	cursor.execute(
		"""
		UPDATE public.award_relationships
		SET emoji_name = COALESCE(NULLIF(emoji_name, ''), split_part(kind, ':', 2)),
			kind = 'wholesome'
		WHERE kind LIKE 'wholesome:%'
		"""
	)


def initialize():
	with connect_with_retry() as connection:
		with connection.cursor() as cursor:
			cursor.execute(
				"""
				CREATE TABLE IF NOT EXISTS public.production_deployment (
					deployment_key VARCHAR(80) PRIMARY KEY,
					initialized_utc INTEGER NOT NULL
				)
				"""
			)
			cursor.execute("SELECT 1 FROM public.production_deployment WHERE deployment_key = 'schema-and-seed'")
			if cursor.fetchone():
				ensure_paypal_schema(cursor)
				ensure_award_effect_schema(cursor)
				print("Production database initialization already completed; auxiliary schemas verified.", flush=True)
				return

			cursor.execute("SELECT to_regclass('public.users')")
			users_table = cursor.fetchone()[0]
			if users_table is not None:
				cursor.execute("SELECT COUNT(*) FROM public.users")
				if cursor.fetchone()[0] != 0:
					raise RuntimeError("Refusing to initialize a non-empty database without a production marker")

			cursor.execute(SCHEMA.read_text(encoding="utf-8"))
			cursor.execute(SEED.read_text(encoding="utf-8"))
			ensure_paypal_schema(cursor)
			ensure_award_effect_schema(cursor)

			for table in ("award_relationships", "badge_defs", "casino_games", "comment_options", "comments", "hat_defs", "lotteries", "modactions", "oauth_apps", "subactions", "submission_options", "submissions", "users"):
				cursor.execute("SELECT pg_get_serial_sequence(%s, 'id')", (f"public.{table}",))
				sequence = cursor.fetchone()[0]
				if sequence:
					cursor.execute(
						f"SELECT setval('{sequence}', GREATEST(COALESCE((SELECT MAX(id) FROM public.{table}), 1), 1), true)"
					)

			cursor.execute(
				"""
				CREATE TABLE IF NOT EXISTS public.production_bootstrap (
					bootstrap_key VARCHAR(80) PRIMARY KEY,
					completed_utc INTEGER NOT NULL,
					user_id INTEGER NOT NULL REFERENCES public.users(id)
				)
				"""
			)
			cursor.execute(
				"""
				INSERT INTO public.production_deployment (deployment_key, initialized_utc)
				VALUES ('schema-and-seed', %s)
				ON CONFLICT (deployment_key) DO NOTHING
				""",
				(int(time.time()),),
			)
		print("Production database initialized with schema and required definitions.", flush=True)


if __name__ == "__main__":
	initialize()
