from emmett import now
from emmett.orm import Model, Field


class TSModel(Model):
    created_at = Field.datetime(default=now, rw=(True, False))
    updated_at = Field.datetime(default=now, update=now, rw=(True, False))
