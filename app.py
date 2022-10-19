from datetime import date

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

##### Set the database URI via SQLAlchemycome.
# protocal + adapter  user_name : password @localhost:port/database_name
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://trello_dev:password123@127.0.0.1:5432/trello"

# create the database object
db = SQLAlchemy(app)
# print(repr(db))
# print(db.__dict__)

# Object represents the database type


class Card(db.Model):
    __tablename__ = "cards"
    # Set the primary key, define that each attribute is also a column in the db table, remember "db" is the object that was created in the previous step.
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    date = db.Column(db.Date)
    status = db.Column(db.String)
    priority = db.Column(db.String)


# Define a custom CLI (terminal) command that can use wirh the Flask program
@app.cli.command("create")
def create():
    db.create_all()
    print("Table created successfully")


@app.cli.command("drop")
def drop_db():
    db.drop_all()
    print("Tables droped")


@app.cli.command("seed")
def seed_db():
    card = [
        Card(
            title="Start the project",
            description="Stage 1 - Create the database",
            status="To Do",
            priority="High",
            date=date.today(),
        ),
        Card(
            title="SQLAlchemy",
            description="Stage 2 - Integrate ORM",
            status="Ongoing",
            priority="High",
            date=date.today(),
        ),
        Card(
            title="ORM Queries",
            description="Stage 3 - Implement several queries",
            status="Ongoing",
            priority="Medium",
            date=date.today(),
        ),
        Card(
            title="Marshmallow",
            description="Stage 4 - Implement Marshmallow to jsonify models",
            status="Ongoing",
            priority="Medium",
            date=date.today(),
        ),
    ]

    db.session.add(card)
    db.session.commit()
    print("Tables seeded")


@app.route("/")
def index():
    print("test")
    return "Hello World!"
