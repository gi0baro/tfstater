import base64

from emmett import Pipe, request, response

from .. import Identity, User, auth


class BasicAuthPipe(Pipe):
    async def pipe(self, next_pipe, **kwargs):
        try:
            auth_data = request.headers.get("authorization", "")
            method, data = auth_data.split(" ")
            assert method == "Basic"
            token = base64.b64decode(data).decode("utf8").split(":", 1)[1]
        except Exception:
            response.status = 401
            return ""
        row = Identity.where(
            lambda m: m.key == token
        ).join("user").select(limitby=(0, 1)).first()
        if not row:
            response.status = 401
            return ""
        request.user = row.user
        return await next_pipe(**kwargs)


class RoleCheckPipe(Pipe):
    def __init__(self, role: User.ROLES):
        self.role = role.value

    async def pipe(self, next_pipe, **kwargs):
        if auth.user.role < self.role:
            response.status = 403
            return {"error": "forbidden"}
        return await next_pipe(**kwargs)


maintainer_only_check = RoleCheckPipe(User.ROLES.maintainer)
