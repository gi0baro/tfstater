from .. import app
from ._pipes import AuthPipe

api = app.module(__name__, "api", url_prefix="api")
api.pipeline = [AuthPipe()]

from . import states
