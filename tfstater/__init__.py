from emmett import App
from emmett.orm import Database
from emmett.sessions import SessionManager
from emmett.tools import Auth, Mailer
from emmett_rest import REST

from .config import load_config
from .idp import Providers

app = App(__name__)
load_config(app)

mailer = Mailer(app)

rest = app.use_extension(REST)

db = Database(app)

from .models.auth import User, Identity
from .models.states import State, StateVersion

auth = Auth(app, db, user_model=User)
db.define_models(Identity, State, StateVersion)

sessions = SessionManager.cookies(app.config.auth.cookies_key, encryption_mode="modern")

idp = Providers(app.config.idp)

from . import api, views, commands
