import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class GameDBO(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(15), nullable=False)
    cmd = db.Column(db.String(10), nullable=False)
    word_id = db.Column(db.Integer, nullable=False)
    word = db.Column(db.String(500), nullable=False)
    lives = db.Column(db.Integer, nullable=False)
    current_letters = db.Column(db.String(200), nullable=False)
    created_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_date = db.Column(db.TIMESTAMP,
                             server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


def init_db():
    app = Flask(__name__)

    sqlalchemy_database_uri = "mysql://{username}:{password}@{hostname}/{databasename}".format(
        username=os.environ['MYSQL_DB_USER'],
        password=os.environ['MYSQL_DB_PWD'],
        hostname=os.environ['MYSQL_DB_HOST_ADDRESS'],
        databasename=os.environ['MYSQL_DB_NAME'],
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = sqlalchemy_database_uri
    app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()


init_db()
