from .idp import Providers


class ConfigurationError(RuntimeError):
    def __init__(self, msg: str):
        super().__init__(f"Configuration error: {msg}")


def load_config(app):
    app.config_from_yaml("app.yml")

    if any (not v for v in [app.config.auth.hmac_key, app.config.auth.cookies_key]):
        raise ConfigurationError(
            "auth.hmac_key and auth.cookies_key values required"
        )

    if app.config.auth.allow_email_login and all(not v for v in [
        app.config.auth.registration_verification,
        app.config.auth.registration_approval
    ]):
        raise ConfigurationError(
            "auth.allow_email_login requires auth.registration_verification "
            "or auth.registration_approval"
        )

    if (
        app.config.auth.registration_verification and
        not app.config.auth.restrict_email_domain
    ):
        raise ConfigurationError(
            "auth.registration_verification requires auth.restrict_email_domain"
        )

    if app.config.auth.registration_verification and not app.config.smtp.server:
        raise ConfigurationError(
            "auth.registration_verification requires smtp.server"
        )

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
    app.config.mailer = app.config.smtp

    idp = {}
    for key in set(
        (app.config.get("idp") or {}).keys()) & set(Providers.registry.keys()
    ):
        element = app.config.idp[key]
        if element and element.get("client_id") and element.get("client_secret"):
            idp[key] = element
    app.config.idp = idp
