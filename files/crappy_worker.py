import os
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from files.helpers.offline_tldextract import configure_tldextract_offline
configure_tldextract_offline()

from files.helpers.const_stateful import const_initialize
from files.helpers.crappy.config import crappy_enabled


def main() -> None:
    database_url = (os.environ.get("DATABASE_URL") or "").strip()
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    engine = create_engine(database_url, pool_pre_ping=True)
    db_session = scoped_session(sessionmaker(bind=engine, autoflush=False))
    const_initialize(db_session)

    # The sanitizer imports stateful emote lists by value. Import the Crappy
    # service only after const_initialize() so the worker sees the populated
    # lists, matching the normal web-process startup order.
    from files.helpers.crappy.retry import (
        defer_transient_provider_failure,
        recover_recent_rate_limited_requests,
    )
    from files.helpers.crappy.service import claim_next_crappy_request, process_crappy_request

    recovery_db = db_session()
    try:
        recovered = recover_recent_rate_limited_requests(recovery_db)
        if recovered:
            print(f"Crappy recovered {recovered} recent rate-limited request(s)", flush=True)
    except Exception as exc:
        recovery_db.rollback()
        print(f"Crappy rate-limit recovery skipped: {type(exc).__name__}: {exc}", flush=True)
    finally:
        recovery_db.close()
        db_session.remove()

    print("Crappy worker started", flush=True)
    while True:
        if not crappy_enabled():
            time.sleep(5)
            continue

        db = db_session()
        try:
            request_id = claim_next_crappy_request(db)
        except Exception as exc:
            db.rollback()
            print(f"Crappy worker waiting for web startup: {type(exc).__name__}: {exc}", flush=True)
            time.sleep(5)
            continue
        finally:
            db.close()
            db_session.remove()

        if request_id is None:
            time.sleep(1)
            continue

        db = db_session()
        try:
            process_crappy_request(db, request_id)
            print(f"Crappy request {request_id} completed", flush=True)
        except Exception as exc:
            if defer_transient_provider_failure(db, request_id, exc):
                retry_after = getattr(exc, "retry_after_seconds", None)
                print(
                    f"Crappy request {request_id} deferred for provider backoff"
                    + (f" ({retry_after}s)" if retry_after else ""),
                    flush=True,
                )
            else:
                print(f"Crappy request {request_id} failed: {type(exc).__name__}: {exc}", flush=True)
        finally:
            db.close()
            db_session.remove()


if __name__ == "__main__":
    main()
