from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#### Any kind of configurations come before any routes.

                                         # protocal + adapter  user_name : password @localhost:port/database_name
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://trello_dev:password123@127.0.0.1:5432/trello'

db = SQLAlchemy(app)

# print(repr(db))
print(db.__dict__)

@app.route('/')
def index():
  return "Hello World!"

