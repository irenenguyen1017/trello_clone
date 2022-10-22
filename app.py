from datetime import date, timedelta

from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import (
    IntegrityError,  # Avoid HTML sending back an error that includes the hash password when the user uses the existing email.
)

app = Flask(__name__)
# combined with `ordered = True` to make the names of the keys sorted in the correct setting order.
app.config["JSON_SORT_KEYS"] = False

##### Set the database URI via SQLAlchemycome.
# protocal + adapter  user_name : password @localhost:port/database_name
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://trello_dev:password123@127.0.0.1:5432/trello"

app.config["JWT_SECRET_KEY"] = "hello there"

# create the database object
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# print(repr(db))
# print(db.__dict__)

# Object represents the database type


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)  # Users must have an email address.
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(
        db.Boolean, default=False
    )  # The default is for non-admin users. That means unless I explicitly say admin is True, it will be False.


class UserSchema(ma.Schema):
    class Meta:  # Enables providing Meta information for the schema to marshmallow.
        fields = ("id", "name", "email", "password", "is_admin")


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
    users = [
        User(
            email="admin@spam.com",
            # password="eggs",
            password=bcrypt.generate_password_hash("eggs").decode("utf-8"),
            is_admin=True,
        ),
        User(
            name="John Cleese",
            email="someone@spam.com",
            # password="12345"
            password=bcrypt.generate_password_hash("12345").decode("utf-8"),
        ),
    ]

    cards = [
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

    db.session.add_all(cards)
    db.session.add_all(users)
    db.session.commit()
    print("Tables seeded")


@app.route("/auth/register/", methods=["POST"])
def auth_register():
    # print(request.json)
    # return ""
    try:
        ## Load the posted user info and parse the JSON
        user_info = UserSchema().load(request.json)
        ## Create a new user model instance from the user_info
        user = User(
            email=user_info["email"],
            password=bcrypt.generate_password_hash(user_info["password"]).decode("utf8"),
            name=user_info["name"],
        )

        ## Add and commit user to DB
        db.session.add(user)
        db.session.commit()
        # Respond to client
        return UserSchema(exclude=["password"]).dump(user), 201
    except IntegrityError:
        return {"error": "Email address already in use"}, 409


@app.route("/auth/login/", methods=["POST"])
def auth_login():
    # Find a user by email address
    stmt = db.select(User).filter_by(email=request.json["email"])
    # Equivalent to:
    # stmt= db.select(User).where(User.email == request.json['email'])
    user = db.session.scalar(stmt)
    # If user exists and password is correct
    if user and bcrypt.check_password_hash(user.password, request.json["password"]):
        # return UserSchema(exclude=["password"]).dump(user)
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        return {"email": user.email, "token": token, "is_admin": user.is_admin}
    else:
        return {"error": "Invalid email or password"}, 401


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
@jwt_required()  # decrypt the token
def all_cards():
    stmt = db.select(Card).order_by(Card.priority.desc(), Card.title)
    cards = db.session.scalars(stmt)
    return CardSchema(many=True).dump(cards)  # `dump` helps convert to json format


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
    return "Hello World!"
