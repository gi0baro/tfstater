from .idp import Providers


def load_config(app):
    app.config_from_yaml("app.yml")

    auth_disabled_routes = ["profile", "download"]
    if not app.config.auth.allow_email_login:
        auth_disabled_routes.extend([
            "email_verification",
            "password_retrieval",
            "password_reset",
            "password_change"
        ])
    app.config.auth.disabled_routes = auth_disabled_routes
    app.config.auth.flash_messages = False
    app.config.auth.remember_option = False
    app.config.auth.single_template = False
    app.config.db.adapter = "postgres"
    app.config.db.big_id_fields = True

    idp = {}
    for key in set(
        (app.config.get("idp") or {}).keys()) & set(Providers.registry.keys()
    ):
        element = app.config.idp[key]
        if element and element.get("client_id") and element.get("client_secret"):
            idp[key] = element
    app.config.idp = idp
