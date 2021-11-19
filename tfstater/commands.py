import click

from . import User, app, db


@app.command("create-maintainer")
@click.argument("email")
@click.argument("password")
def cmd_create_maintainer(email, password):
    with db.connection():
        res = User.create(
            email=email,
            password=password,
            role=User.ROLES.maintainer.value
        )
        if not res.id:
            return
        res.id.allow()
        db.commit()
