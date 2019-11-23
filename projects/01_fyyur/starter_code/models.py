from datetime import datetime
from flask_moment import Moment
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Models
class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(1200))
    facebook_link = db.Column(db.String(1200))
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(1200))
    image_link = db.Column(db.String(1200))
    show = db.relationship('Show', backref='Artist', lazy=True)


class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(1200))
    facebook_link = db.Column(db.String(1200))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(1200))
    image_link = db.Column(db.String(1200))
    show = db.relationship('Show', backref='Venue', lazy=True)


class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    artist = db.relationship('Artist', backref=db.backref(
        'artist_obj', cascade="all,delete"))
    venue = db.relationship('Venue', backref=db.backref(
        'venue_obj', cascade="all,delete"))