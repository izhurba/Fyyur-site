#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import logging
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Venue, Show, Artist

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.app = app
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venue_areas = Venue.query.distinct(Venue.city, Venue.state).all()
    venues = Venue.query.all()
    data = []
    for area in venue_areas:
        data.append({
            "city": area.city,
            "state": area.state,
            "venues": [{
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len([show for show in venue.shows if show.start_time > datetime.now()])
            } for venue in venues if
                venue.city == area.city and venue.state == area.state]
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    results = Venue.query.filter(Venue.name.ilike(
        '%{}%'.format(request.form['search_term']))).all()
    response = {
        "count": len(results),
        "data": []
    }
    for venue in results:
        response["data"].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len([show for show in venue.shows if show.start_time > datetime.now()])
        })

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    past_shows = []
    upcoming_shows = []

    shows = venue.shows
    for show in shows:
        show_info = {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        }
        if show.start_time >= datetime.now():
            upcoming_shows.append(show_info)
        else:
            past_shows.append(show_info)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website_link": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    try:
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            facebook_link=form.facebook_link.data,
            genres=form.genres.data,
            website_link=form.website_link.data,
            image_link=form.image_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data,
        )

        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except ValueError as e:
        if app.debug:
            print(e)
        db.session.rollback()
        flash('An error has occurred. Venue ' +
              request.form['name'] + ' could not be added.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    try:
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully deleted!')
    except:
        db.session.rollback()
        flash('Venue ' + venue.name + ' could not be deleted.')
    finally:
        db.session.close()
        return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = Artist.query.with_entities(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    results = Artist.query.filter(Artist.name.ilike(
        '%{}%'.format(request.form['search_term']))).all()
    response = {
        "count": len(results),
        "data": []
    }
    for artist in results:
        response["data"].append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len([show for show in artist.shows if show.start_time > datetime.now()])
        })
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    shows = artist.shows
    past_shows = []
    upcoming_shows = []
    for show in shows:
        show_info = {
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        }
        if show.start_time >= datetime.now():
            upcoming_shows.append(show_info)
        else:
            past_shows.append(show_info)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website_link": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_artist.html', artist=data)


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    try:
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            genres=form.genres.data,
            phone=form.phone.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data
        )

        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except ValueError as e:
        if app.debug:
            print(e)
        db.session.rollback()
        flash('An error occurred. Artist ' +
              artist.name + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/artists/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):
    artist = Artist.query.get(artist_id)
    try:
        db.session.delete(artist)
        db.session.commit()
        flash('Artist ' + artist.name + ' was successfully deleted!')
    except:
        db.session.rollback()
        flash('Artist ' + artist.name + ' could not be deleted.')
    finally:
        db.session.close()
        return jsonify({'success': True})

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(request.form)

    try:
        form.populate_obj(artist)
        db.session.commit()
        flash("Artist {} is updated successfully".format(artist.name))
    except:
        db.session.rollback()
        flash("Artist {} isn't updated successfully".format(artist.name))
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(request.form)

    try:
        form.populate_obj(venue) #Per code review, I decided this was cleaner to use
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully updated!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              venue.name + ' could not be updated.')
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.all()
    data = []
    for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
            })
    return render_template('pages/shows.html', shows=data)



@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm()
    
    try:
        show = Show(
            artist_id = form.artist_id.data,
            venue_id = form.venue_id.data,
            start_time = form.start_time.data,
            upcoming = (datetime.now() < form.start_time.data)
        )
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except ValueError as e:
        if app.debug:
            print(e)
        db.session.rollback()
        flash('An error occured. Show could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#


# specify port manually:

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4455)
