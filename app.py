import os
import click

from app import create_app, db


app = create_app(os.environ.get("DANA_CONFIG", "development"))


@app.cli.command()
def initdb():
    """Initialize the database."""
    click.echo('Initalize the db')
    db.drop_all()
    db.create_all()

if __name__ == "__main__":
    initdb()
    app.run(port=5000, use_reloader=True, extra_files=["app/api.yml"])












