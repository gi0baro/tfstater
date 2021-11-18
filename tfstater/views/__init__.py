from .. import app, auth, db, sessions

views = app.module(__name__, "views")
views.pipeline = [sessions, db.pipe, auth.pipe]


@app.route(methods="get", output="bytes")
async def _health():
    return b""


from . import accounts, main
