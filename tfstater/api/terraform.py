from emmett import Pipe, request, response
from emmett.serializers import Serializers
from emmett.tools import service

from .. import db
from ..helpers import StateLockedException
from ..models.states import State
from ..s3 import get_object, put_object
from . import api
from ._pipes import BasicAuthPipe


class CType(Pipe):
    async def open(self):
        response.content_type = "application/json"


_json_dump = Serializers.get_for("json")

terraform = api.module(__name__, "terraform", url_prefix="terraform")
terraform.pipeline = [BasicAuthPipe(), CType()]


@terraform.route("/<any:name>", methods="get", output="bytes")
async def get_state_by_name(name: str):
    rv = b"{}"
    row = State.get(name=name)
    if not row or not row.file_path:
        response.status = 404
        return rv
    try:
        rv = await get_object(row.file_path)
    except Exception:
        response.status = 404
    return rv


@terraform.route("/<any:name>/lock", methods="post")
@service.json
async def lock_state(name: str):
    params = await request.body_params
    acquired, row = State.get_or_create_locked(name, request.user, params.ID)
    if not acquired:
        response.status = 409
    return {
        "Created": row.locked_at,
        "ID": row.lock_id,
        "Info": params.Info,
        "Operation": params.Operation,
        "Path": params.Path,
        "Version": params.Version,
        "Who": row.lock_owner.email
    }


@terraform.route("/<any:name>/lock", methods="delete", output="bytes")
async def unlock_state(name: str):
    # NOTE: if ID is missing from params is a force unlock
    params = await request.body_params
    if not State.unlock({"name": name}, params.ID):
        response.status = 409
    return b"{}"


# NOTE: this route should be the last defined to avoid catching also `lock_state`
@terraform.route("/<any:name>", methods="post", output="bytes")
async def update_state_by_name(name: str):
    try:
        with State.lock(name, request.user, request.query_params.ID) as state:
            params = await request.body_params
            try:
                with db.atomic():
                    revision = state.versions.create(
                        version=params.serial,
                        publisher=request.user
                    )
            except Exception:
                raise StateLockedException
            await put_object(
                revision.id.object_store_path,
                _json_dump(params)
            )
    except StateLockedException:
        response.status = 409
    return b"{}"
