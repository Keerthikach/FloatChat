from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional, Dict
from .models import SessionContext, SessionUpsert

class SimpleSessionStore:
    def __init__(self):
        self._db: Dict[str, SessionContext] = {}

    def create_or_update(self, upsert: SessionUpsert) -> SessionContext:
        now = datetime.now(timezone.utc)
        sid = upsert.session_id or str(uuid4())

        if sid in self._db:
            cur = self._db[sid]

            updates: Dict[str, object] = {"updated_at": now}
            if upsert.user_id is not None:
                updates["user_id"] = upsert.user_id
            if upsert.preferred_units is not None:
                updates["preferred_units"] = upsert.preferred_units
            if upsert.notes is not None:
                updates["notes"] = upsert.notes

            ctx = cur.model_copy(update=updates)
        else:
            ctx = SessionContext(
                session_id=sid,
                user_id=upsert.user_id,
                preferred_units=upsert.preferred_units or "metric",
                notes=upsert.notes,
                created_at=now,
                updated_at=now,
            )

        self._db[sid] = ctx
        return ctx

    def get(self, session_id: str) -> Optional[SessionContext]:
        return self._db.get(session_id)

