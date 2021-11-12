import uuid

from contextlib import contextmanager

from emmett import now
from emmett.orm import Field, belongs_to, before_insert, has_many, refers_to, rowattr

from ..helpers import StateLockedException
from . import TSModel


class State(TSModel):
    has_many({"versions": "StateVersion"})
    refers_to({"lock_owner": "User"})

    name = Field(notnull=True)
    lock_id = Field(length=36)
    locked_at = Field.datetime()

    validation = {
        "locked_at": {"allow": "empty"}
    }

    indexes = {
        "name_uniq": {"fields": ["name"], "unique": True}
    }

    @classmethod
    def get_or_create_locked(cls, name, lock_owner, lock_id):
        try:
            with cls.db.atomic():
                res = cls.create(
                    name=name,
                    lock_id=lock_id,
                    lock_owner=lock_owner,
                    locked_at=now()
                )
            return True, res.id
        except Exception:
            pass
        return cls.get_with_lock(name, lock_owner, lock_id=lock_id)

    @classmethod
    def get_locked(cls, name, lock_id):
        return cls.get(name=name, lock_id=lock_id)

    @classmethod
    def get_with_lock(cls, name, lock_owner, lock_id=None):
        lock_id = lock_id or uuid.uuid4().hex
        res = cls.where(
            lambda m: (m.name == name) & (m.lock_id == None)
        ).update(
            lock_id=lock_id,
            lock_owner=lock_owner,
            locked_at=now()
        )
        row = cls.get(name=name)
        if not res:
            return False, row
        return True, row

    @classmethod
    def unlock(cls, name, existing_lock_id=None):
        dbset = cls.where(lambda m: m.name == name)
        if existing_lock_id:
            dbset = dbset.where(lambda m: m.lock_id == existing_lock_id)
        else:
            dbset = dbset.where(lambda m: m.lock_id != None)
        res = dbset.update(
            lock_id=None,
            lock_owner=None,
            locked_at=None
        )
        return bool(res)

    @classmethod
    @contextmanager
    def lock(cls, name, lock_owner, lock_id=None):
        with cls.db.atomic():
            if lock_id:
                row = cls.get_locked(name, lock_id)
                if not row:
                    raise StateLockedException
            else:
                lock_acquired, row = cls.get_with_lock(name, lock_owner=lock_owner)
                if not lock_acquired:
                    raise StateLockedException
            try:
                yield row
            finally:
                if not lock_id:
                    cls.where(
                        lambda m: (m.id == row.id) & (m.lock_id == row.lock_id)
                    ).update(
                        lock_id=None,
                        lock_owner=None,
                        locked_at=None
                    )

    @classmethod
    def get_latest(cls, name):
        return cls.db.where((StateVersion.state == cls.id) & (cls.name == name)).select(
            orderby=~StateVersion.version, limitby=(0, 1)
        ).first()

    @rowattr("latest_version")
    def _latest_version(self, row):
        return row.versions.select(
            orderby=~StateVersion.version, limitby=(0, 1)
        ).first()

    @rowattr("file_path")
    def _file_path(self, row):
        return row.latest_version.object_store_path if row.latest_version else None


class StateVersion(TSModel):
    belongs_to("state")
    refers_to({"publisher": "User"})

    version = Field.bigint(notnull=True, default=0)
    object_store_path = Field(notnull=True, rw=(True, False))

    validation = {
        "object_store_path": {"allow": "empty"}
    }

    indexes = {
        "uniq_version": {"fields": ["state", "version"], "unique": True}
    }

    @before_insert
    def _gen_path_if_needed(self, fields):
        if not fields.get("object_store_path"):
            state = State.get(fields.state)
            fields.object_store_path = f"{state.name}/{uuid.uuid4().hex}"
