import base64
import uuid

from enum import Enum

from emmett.orm import Field, before_insert, belongs_to, has_many
from emmett.tools.auth.models import AuthUserBasic

from .. import app
from . import TSModel


def _validate_email(value):
    if app.config.auth.restrict_email_domain:
        if not value.endswith(app.config.auth.restrict_email_domain):
            return value, "Email address not allowed"
    return value, None


class User(AuthUserBasic):
    class ROLES(int, Enum):
        member = 0
        maintainer = 10

    has_many(
        {"identities": "Identity"},
        {"locked_states": "State.lock_owner"},
        {"pushed_states": "StateVersion.publisher"}
    )

    role = Field.int(notnull=True)

    default_values = {
        "role": ROLES.member.value
    }

    validation = {
        "email": {"is": "email", "custom": _validate_email},
        "role": {"in": [role.value for role in ROLES]}
    }

    indexes = {
        "email_uniq": {"fields": ["email"], "unique": True}
    }


class Identity(TSModel):
    tablename = "identities"

    belongs_to("user")

    key = Field.string()

    indexes = {
        "key_uniq": {"fields": ["key"], "unique": True}
    }

    @before_insert
    def _gen_key(self, fields):
        fields.key = base64.b64encode(
            uuid.uuid4().bytes + uuid.uuid4().bytes
        ).decode("utf8")
