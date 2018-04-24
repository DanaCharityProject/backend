import os

from app import create_app, db

if __name__ == "__main__":
    app = create_app(os.environ.get("DANA_CONFIG", "development"))

    app.run(port=5000, use_reloader=True, extra_files=["app/api.yml"])



@app.cli.command()
def initdb():
    """Initialize the database."""
    click.echo('Init the db')
    db.drop_all()
    db.create_all()

    '''session.add_all([ User(id=1, username='Eilonwy', password_hash='foobar'),
        User(id=2, username='Taran', password_hash='prydain'),
        User(id=3, username='Gurgi', password_hash='caer'),
        ])'''

    '''session.add_all([ CommunityResource(id=1, charity_number=101, name="Charity1", y=43.6532, x=79.3832, contact_name="John Smith", email="JSmith@gmail.com",
        phone_number="4165555555", address="1 Yonge ave", website="www.charity1.org", image_uri="", verified=false)
        )])'''

    #address line 1, address line 2 ....

