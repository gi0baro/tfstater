import base64
import uuid

from emmett.orm import Field, before_insert, belongs_to, has_many
from emmett.tools.auth.models import AuthUserBasic

from . import TSModel


class User(AuthUserBasic):
    has_many(
        {"identities": "Identity"},
        {"locked_states": "State.lock_owner"},
        {"pushed_states": "StateVersion.publisher"}
    )


class Identity(TSModel):
    tablename = "identities"

    belongs_to("user")

    key = Field.string()

    indexes = {
        "key_uniq": {"fields": ["key"], "unique": True}
    }

    @before_insert
    def _gen_key(self, fields):
        fields.key = base64.b64encode(uuid.uuid4().bytes).decode("utf8")
