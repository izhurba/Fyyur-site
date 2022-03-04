from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
db = SQLAlchemy()


def database(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String, nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean,nullable=False, default=False)
    seeking_description = db.Column(db.String(500), default='')
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)
    shows = db.relationship('Show',backref='venue',lazy=True)

    def get_info(self):
        return {
            'id': self.id,
            'name' :self.name,
            'genres' : self.genres,
            'address' :self.address,
            'city' :self.city,
            'state' :self.state,
            'phone' :self.phone,
            'website_link' :self.website_link,
            'facebook_link':self.facebook_link,
            'seeking_talent' :self.seeking_talent,
            'seeking_description' :self.seeking_description,
            'image_link' :self.image_link
        }



class Artist(db.Model):
    __tablename__ = 'Artist'

    id = Column(Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String, nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,nullable=False, default=False)
    seeking_description = db.Column(db.Text)
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)
    shows = db.relationship('Show',backref='artist',lazy=True,cascade="save-update, merge, delete")

    def get_info(self):
        return {
            'id': self.id,
            'name' :self.name,
            'state' :self.state,
            'genres' : self.genres,
            'city' :self.city,
            'phone' :self.phone,
            'website_link' :self.website_link,
            'facebook_link':self.facebook_link,
            'seeking_venue' :self.seeking_venue,
            'seeking_description' :self.seeking_description,
            'image_link' :self.image_link,
            'upcoming_shows_count' :self.upcoming_shows_count,
            'past_shows_count' : self.past_shows_count,
            'shows' :self.shows
        }


class Show(db.Model):
    __tablename__ = 'shows'
    
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
    venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)
    upcoming = db.Column(db.Boolean, nullable=False, default=True)

    def get_info(self):
        return{
            'venue_id' :self.venue_id,
            'venue_name' :self.Venue.name,
            'artist_id' :self.artist_id,
            'artist_name' :self.Artist.name,
            'artist_image_link' :self.Artist.image_link,
            'start_time' :self.start_time
        }

    def get_artist_info(self):
        return{
            'artist_id' :self.venue_id,
            'artist_name' :self.Artist.name,
            'artist_image_link' :self.Artist.image_link,
            'start_time' :self.start_time

        }
 
    def get_venue_info(self):
        return{
            'venue_id' :self.venue_id,
            'venue_name' :self.Venue.name,
            'venue_image_link' :self.Venue.image_link,
            'start_time' :self.start_time
            
        }
