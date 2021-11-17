from emmett.tools.service import ServicePipe

from .. import app, auth, db, sessions

api = app.module(__name__, "api")
api.pipeline = [db.pipe]

rest_api = api.module(__name__, "rest", url_prefix="api")
rest_api.pipeline = [ServicePipe("json"), sessions, auth.pipe]

from . import states, terraform
