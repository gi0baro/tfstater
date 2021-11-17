from emmett import response
from emmett_rest import RESTModule

from .. import State, auth
from . import rest_api
from ._pipes import maintainer_only_check


class StatesModule(RESTModule):
    def init(self):
        self.create_pipeline.append(maintainer_only_check)
        self.delete_pipeline.append(maintainer_only_check)


states = rest_api.rest_module(
    __name__, "states", State,
    url_prefix="states",
    enabled_methods=["index", "create", "delete"],
    module_class=StatesModule
)


@states.route("/<int:rid>/lock", methods="post", pipeline=[maintainer_only_check])
async def lock_state(rid):
    acquired, row = State.get_with_lock({"id": rid}, auth.user)
    if not acquired:
        response.status = 409
        return {"error": "Unable to acquire lock"}
    response.status = 201
    return {
        "lock_id": row.lock_id,
        "lock_owner": row.lock_owner,
        "locked_at": row.locked_at
    }


@states.route("/<int:rid>/lock", methods="delete", pipeline=[maintainer_only_check])
async def unlock_state(rid):
    unlocked = State.unlock({"id": rid})
    if not unlocked:
        response.status = 409
        return {"error": "Unable to unlock"}
    return {}
