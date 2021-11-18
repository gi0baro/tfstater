import click

from . import User, app, db


@app.command("create-maintainer")
@click.argument("email")
@click.argument("password")
def cmd_create_maintainer(email, password):
    with db.connection():
        User.create(
            email=email,
            password=password,
            role=User.ROLES.maintainer
        )
        db.commit()
