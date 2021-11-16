from .. import app, auth, db, sessions

views = app.module(__name__, "views")
views.pipeline = [sessions, db.pipe, auth.pipe]


from . import accounts, main
