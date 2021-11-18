from emmett import Injector, abort, url, redirect, request

from .. import User, app, auth, db, idp
from ..idp import ExchangePipe
from . import views
from .main import MainContext


class AuthHelpers(Injector):
    namespace = "auth_helpers"

    @property
    def allow_email_login(self):
        return app.config.auth.allow_email_login

    @property
    def idps(self):
        return idp.available()


auth_routes = auth.module(
    __name__,
    url_prefix="account",
    pipeline=views.pipeline,
    injectors=[AuthHelpers()]
)


@auth_routes.after_login
def _after_login(form):
    redirect(url("views.index"))


@auth_routes.after_registration
def _after_registration(form, user, logged_in):
    if logged_in:
        redirect(url("views.index"))
    redirect(url("account.login"))


@auth_routes.after_email_verification
def _after_email_verification(user):
    redirect(url('account.login'))


if "password_change" in auth_routes.enabled_routes:
    @auth_routes.password_change(injectors=[MainContext()])
    async def password_change():
        user = User.get(auth.user.id)
        if not user.password:
            return {"message": "You logged in with an external identity provider"}
        return await auth_routes._password_change()


if github_idp_provider := idp.get("github"):
    @auth_routes.route()
    async def github():
        scheme = request.headers.get("x-forwarded-proto") or request.scheme
        github_idp_provider.authorize(
            url(".github_exchange", scheme=scheme)
        )

    @auth_routes.route(
        "/github/exchange", pipeline=[ExchangePipe(github_idp_provider)]
    )
    async def github_exchange(user, role, teams):
        internal_role = User.ROLES.member.value
        if github_idp_provider.config.claim_roles:
            if role not in github_idp_provider.config.claim_roles:
                abort(401)
        if github_idp_provider.config.claim_teams:
            if not set(github_idp_provider.config.claim_teams) & set(teams):
                abort(401)
        if github_idp_provider.config.match_roles:
            if matched_role := github_idp_provider.config.match_roles.get(role):
                internal_role = User.ROLES[matched_role]
        if github_idp_provider.config.match_teams:
            matched_roles = []
            for team in teams:
                if matched_role := github_idp_provider.config.match_teams.get(team):
                    matched_roles.append(User.ROLES[matched_role])
            if matched_roles:
                internal_role = max([role.value for role in matched_roles])
        try:
            with db.atomic():
                if not User.table.insert(
                    email=user["email"], password="", role=internal_role
                ):
                    abort(401)
        except Exception:
            if not User.where(
                lambda u: u.email == user["email"]
            ).update(password="", role=internal_role):
                abort(401)

        auth.ext.login_user(User.get(email=user["email"]))
        redirect(url("views.index"))
