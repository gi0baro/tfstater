from emmett import App
from emmett.orm import Database
from emmett.tools.auth import Auth

app = App(__name__)
app.config_from_yaml("app.yml")
# app.config.db.big_id_fields = True


db = Database(app)

from .models.auth import User, Identity
from .models.states import State, StateVersion

auth = Auth(app, db, user_model=User)
db.define_models(Identity, State, StateVersion)

from . import api
