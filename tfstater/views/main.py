from emmett import Injector, request, url, redirect

from emmett.pipeline import RequirePipe
from emmett.tools import requires

from .. import User, auth
from . import views


class MainContext(Injector):
    namespace = "ctx"

    @property
    def user(self):
        return auth.user


@views.route("/", injectors=[MainContext()])
@requires(auth.is_logged, lambda: redirect(url("auth.login")))
async def index():
    return {}


@views.route(injectors=[MainContext()])
@requires(auth.is_logged, lambda: redirect(url("auth.login")))
async def settings():
    can_manage_users = auth.user.role == User.ROLES.maintainer
    users = User.all().select() if can_manage_users else []
    return {
        "api_keys": auth.user.identities(),
        "can_manage_users": can_manage_users,
        "users": users
    }


actions = views.module(__name__, "actions", url_prefix="settings/actions")
actions.pipeline = [RequirePipe(auth.is_logged, lambda: redirect(url("auth.login")))]
actions.injectors = [MainContext()]


@actions.route()
async def new_identity():
    auth.user.identities.create()
    redirect(url('views.settings'))


@actions.route("/delete_identity/<int:identity_id>")
async def delete_identity(identity_id):
    auth.user.identities.where(lambda m: m.id == identity_id).delete()
    redirect(url('views.settings'))


@actions.route("/edit_user/<int:user_id>")
@requires(
    lambda: auth.user.role == User.ROLES.maintainer,
    lambda: redirect((url("view.settings")))
)
async def edit_user(user_id):
    if user_id != auth.user.id:
        User.where(lambda u: u.id == user_id).validate_and_update(
            role=request.query_params.role
        )
    redirect(url('views.settings'))


@actions.route("/delete_user/<int:user_id>")
@requires(
    lambda: auth.user.role == User.ROLES.maintainer,
    lambda: redirect((url("view.settings")))
)
async def delete_user(user_id):
    if user_id != auth.user.id:
        User.where(lambda u: u.id == user_id).delete()
    redirect(url('views.settings'))
