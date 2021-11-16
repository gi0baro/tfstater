from emmett import url, redirect

from emmett.tools import requires

from .. import auth
from . import views


@views.route("/")
@requires(auth.is_logged, lambda: redirect(url("auth.login")))
async def index():
    return {}
