from .idp import Providers


def load_config(app):
    app.config_from_yaml("app.yml")
    app.config.auth.disabled_routes = [
        "profile",
        "password_retrieval",
        "password_reset",
        "password_change"
    ]
    app.config.auth.flash_messages = False
    app.config.auth.registration_verification = False
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
