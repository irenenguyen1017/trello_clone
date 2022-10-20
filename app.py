from datetime import date

from flask import Flask, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config ['JSON_SORT_KEYS'] = False # combined with `ordered = True` to make the names of the keys sorted in the correct setting order.

##### Set the database URI via SQLAlchemycome.
# protocal + adapter  user_name : password @localhost:port/database_name
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://trello_dev:password123@127.0.0.1:5432/trello"

# create the database object
db = SQLAlchemy(app)
ma = Marshmallow(app)

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


class CardSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "title",
            "description",
            "status",
            "priority",
            "date",
        )

        ordered = True


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


# @app.cli.command("all_cards")
# def all_cards():
# select * from cards;
# cards = Card.query.all() # old way query

# New way queries:
# stmt = db.select(Card) #Just build the query
# cards = db.session.scalars(stmt).all() #execute the query

# (Or this block code)
# cards = db.session.scalars(stmt)
# for card in cards:
#     print(card)

# Choice specific columns
# stmt = db.select(Card.title, Card.status)
# cards = db.session.execute(stmt).all() # execute produces tuples, while scalar is not.

# (Or this block code)
# stmt = db.select(Card.title, Card.status)
# cards = db.session.execute(stmt)
# for card in cards:
#     print(card)

# stmt = db.select(Card).where(Card.status == "Ongoing", Card.priority == "High") # `,` present AND operator
# stmt = db.select(Card).where(Card.id > 2)
# stmt = db.select(Card).where(db.or_(Card.status == "To Do", Card.priority == "High")) # db.or_ present OR operator
# stmt = db.select(Card).filter_by(status="To Do") # equivalent to `stmt = db.select(Card).where(Card.status == "To Do")`.
# stmt = db.select(Card).order_by(Card.priority, Card.title) # ascending order
# stmt = db.select(Card).order_by(Card.priority.desc(), Card.title) # decending order
# cards = db.session.scalars(stmt)
# for card in cards:
#     print(card.title, card.priority)

# print(cards)
# print(cards[0].__dict__)


@app.route("/cards/")
def all_cards():
    stmt = db.select(Card).order_by(Card.priority.desc(), Card.title)
    cards = db.session.scalars(stmt)
    return CardSchema(many=True).dump(cards)


@app.cli.command("first_card")
def first_card():
    # select * from cards limit 1;
    # card = Card.query.first()   # old way query
    stmt = db.select(Card).limit(1)
    print(stmt)
    card = db.session.scalar(stmt)
    print(card.__dict__)


@app.cli.command("count_ongoing")
def count_ongoing():
    stmt = db.select(db.func.count()).select_from(Card).filter_by(status="Ongoing")
    # cards = db.session.scalars(stmt).all() # return the number of cards in list
    cards = db.session.scalar(stmt)
    print(cards)


@app.route("/")
def index():
    print("test")
    return "Hello World!"
