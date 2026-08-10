import os
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from files.helpers.crappy.config import crappy_enabled
from files.helpers.crappy.install import ensure_crappy_account, install_crappy
from files.helpers.crappy.service import claim_next_crappy_request, process_crappy_request


def main() -> None:
    database_url = (os.environ.get("DATABASE_URL") or "").strip()
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    engine = create_engine(database_url, pool_pre_ping=True)
    db_session = scoped_session(sessionmaker(bind=engine, autoflush=False))
    install_crappy(engine, db_session, enabled=crappy_enabled())

    print("Crappy worker started", flush=True)
    while True:
        if not crappy_enabled():
            time.sleep(5)
            continue

        db = db_session()
        try:
            ensure_crappy_account(db)
            db.commit()
            request_id = claim_next_crappy_request(db)
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
            print(f"Crappy request {request_id} failed: {type(exc).__name__}: {exc}", flush=True)
        finally:
            db.close()
            db_session.remove()


if __name__ == "__main__":
    main()
