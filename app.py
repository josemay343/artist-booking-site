#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value

  return babel.dates.format_datetime(date, format)

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
  data=[]

  venues = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  for venue in venues:
    venue_city = db.session.query(Venue.id, Venue.name).filter(Venue.city == venue[0]).filter(Venue.state == venue[1])
    data.append({
      'city':venue[0],
      'state': venue[1],
      'venues': venue_city
    })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues_search = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
  response = {
    'count': len(venues_search),
    'data': venues_search
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
  if venue.genres is not None:
    venue.genres = venue.genres.split(',')
    venue.genres = [item.replace('{', '').replace('}','') for item in venue.genres]
  else:
    venue.genres = []

  today = datetime.now()

  shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).all()
  past_shows = []
  upcoming_shows = []

  for show in shows:
    artist = db.session.query(Artist).filter(Artist.id == show.artist_id).first()

    show_details = {
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': show.start_time
    }

    if show.start_time < today:
      past_shows.append(show_details)
    else:
      upcoming_shows.append(show_details)

  print(past_shows)
  data = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'city': venue.city,
    'state': venue.state,
    'address': venue.address,
    'phone': venue.phone,
    'website': venue.website,
    'image_link': venue.image_link,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'past_shows': past_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows': upcoming_shows,
    'upcoming_shows_count': len(upcoming_shows)
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
  try:
    new_venue = Venue(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      address = request.form.get('address'),
      phone = request.form.get('phone'),
      genres = request.form.getlist('genres'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website_link'),
      image_link = request.form.get('image_link'),
      seeking_talent = True if request.form.get('seeking_talent') == 'y' else False,
      seeking_description = request.form.get('seeking_description')
    )

    db.session.add(new_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  try:
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Venue ' + venue.name + ' was not deleted!')

  finally:
    db.session.close()
  
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artist = db.session.query(Artist.name, Artist.id)
  return render_template('pages/artists.html', artists=artist)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artist_search = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()
  response={
    "count": len(artist_search),
    "data": artist_search
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()
  print(artist)
  if artist.genres is not None:
    artist.genres = artist.genres.split(',')
    artist.genres = [item.replace('{', '').replace('}','') for item in artist.genres]
  else:
    artist.genres = []

  today = datetime.now()

  shows = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).all()
  past_shows = []
  upcoming_shows = []

  for show in shows:
    venue = db.session.query(Venue).filter(Venue.id == show.venue_id).first()

    show_details = {
      'venue_id': venue.id,
      'venue_name': venue.name,
      'venue_image_link': venue.image_link,
      'start_time': show.start_time
    }

    if show.start_time < today:
      past_shows.append(show_details)
    else:
      upcoming_shows.append(show_details)

  data = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'image_link': artist.image_link,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'past_shows': past_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows': upcoming_shows,
    'upcoming_shows_count': len(upcoming_shows)
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
  form = ArtistForm(obj=artist)
  form.genres.data = artist.genres

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)

  try:
    artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
    form.populate_obj(artist)
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully updated!')

  except:
    db.session.rollback()
    print(sys.exc_info)
    flash('An error occurred. Artist ' + artist.name + ' could not be edited.')
    
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
  form = VenueForm(obj=venue)
  form.genres.data = venue.genres

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)

  try:
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
    form.populate_obj(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully updated!')

  except:
    db.session.rollback()
    print(sys.exc_info)
    flash('An error occurred. Venue ' + venue.name + ' could not be edited.')
    
  finally:
    db.session.close()
    
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    new_artist = Artist(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),
      genres = request.form.getlist('genres'),
      image_link = request.form.get('image_link'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website'),
      seeking_venue = True if request.form.get('seeking_venue') == 'y' else False,
      seeking_description = request.form.get('seeking_description')
    )
    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

  finally:
      db.session.close()

  return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['POST'])
def delete_artist(artist_id):
  try:
    artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
    db.session.delete(artist)
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully deleted!')

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Artist ' + artist.name + ' was not deleted!')

  finally:
    db.session.close()
  
  return render_template('pages/home.html')
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = db.session.query(Show).join(Venue).join(Artist).order_by(Show.start_time.asc()).all()
  print(shows)
  for show in shows:
    data.append({
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time
    })
 
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    new_show = Show(
      artist_id = request.form.get('artist_id'),
      venue_id = request.form.get('venue_id'),
      start_time = request.form.get('start_time')
    )
    db.session.add(new_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
