#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from flask_migrate import Migrate
from datetime import datetime, timedelta
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship("Show", backref="venue_shows")

    def venue_city_state(self):
      return {
        'city': self.city,
        'state': self.state,
      }

    def venue_detail(self):
      return {
        'id': self.id,
        'name': self.name,
        'num_upcoming_shows': 0,
      }

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship("Show", backref="artist_shows")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  venue = db.relationship("Venue", backref="shows_venue")
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  artist = db.relationship("Artist", backref="shows_artist")


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format = "EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format = "EE MM, dd, y h:mma"
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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  fullvenue = Venue.query.all()
  venue = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
  return render_template('pages/venues.html', areas=venue, venue=fullvenue)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venueItem = request.form.get('search_term', '')
  response = Venue.query.filter(Venue.name.like('%'+venueItem+'%')).all()
  venuecount = Venue.query.filter(Venue.name.like('%'+venueItem+'%'))
  numberofvenue = venuecount.count()
  count = {
     "count": numberofvenue,
  }
  return render_template('pages/search_venues.html', results=count, data=response,
   search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  alldata = []
  pastshows = []
  upcoming_shows = []
  venues = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venues.id)
  now = datetime.now()
  for show in shows:
      if show.start_time < now:
        pastshows.append({
        "artist_id": show.artist_id,
        "artist_name": Artist.query.get(show.artist_id).name,
        "artist_image_link": Artist.query.get(show.artist_id).image_link,
        "start_time": format_datetime(show.start_time.strftime("%Y-%m-%d %H:%M:%S"))
      })
      else:
         upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": Artist.query.get(show.artist_id).name,
        "artist_image_link": Artist.query.get(show.artist_id).image_link,
        "start_time": format_datetime(show.start_time.strftime("%Y-%m-%d %H:%M:%S"))
      })
   
  venueData ={
    "id": venues.id,
    "name": venues.name,
    "genres": venues.genres,
    "address": venues.address,
    "city": venues.city,
    "state": venues.state,
    "phone": venues.phone,
    "website": venues.website,
    "facebook_link": venues.facebook_link,
    "seeking_talent": venues.seeking_talent,
    "seeking_description": venues.seeking_description,
    "image_link": venues.image_link,
    "past_shows": pastshows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(pastshows),
    "upcoming_shows_count": len(upcoming_shows),  
  }
  alldata.insert(venue_id, venueData)
  data = list(filter(lambda d: d['id'] == venue_id, alldata))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = request.form
  name = ''
  try:
    name = form['name']
    print('Name =',name)
    genres = form['genres']
    address = form['address']
    city = form['city']
    state = form['state']
    phone = form['phone']
    website = form['website']   
    facebook_link = form['facebook_link']
    print('FaceBOOK',facebook_link)
    if "seeking_talent" in form:
      seeking_talent = form['seeking_talent']
      if seeking_talent == 'y':
        seeking_talent = True
    else:
      seeking_talent = False
    seeking_description = request.form['seeking_description']
    image_link = request.form['image_link']
    venue = Venue(name=name,genres=genres,address=address,city=city,state=state,phone=phone,
    website=website,facebook_link=facebook_link,seeking_talent=seeking_talent,
    seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  finally:
    db.session.close()
    return render_template('pages/home.html')
  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.group_by(Artist.id, Artist.name).all()
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artistMember = request.form.get('search_term', '')
  queryresponse = Artist.query.filter(Artist.name.like('%'+artistMember+'%')).all()
  artists = Artist.query.filter(Artist.name.like('%'+artistMember+'%'))
  numberofvenue = artists.count()
  count = {
     "count": numberofvenue,
  }
  data =[]
  for i in queryresponse:
    data.append({
      "id": i.id,
      "name": i.name,
    })
  response = {
    "count": numberofvenue,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  past_shows = []
  upcoming_shows =[]
  alldata = []
  artists = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artists.id)
  now = datetime.now()
  for show in shows:
      if show.start_time < now:
        past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": Venue.query.get(show.venue_id).name,
        "venue_image_link": Artist.query.get(show.venue_id).image_link,
        "start_time": format_datetime(show.start_time.strftime("%Y-%m-%d %H:%M:%S"))
      })
      else:
         upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": Venue.query.get(show.venue_id).name,
        "venue_image_link": Artist.query.get(show.venue_id).image_link,
        "start_time": format_datetime(show.start_time.strftime("%Y-%m-%d %H:%M:%S"))
      })
  respnse = {
    "id": artists.id,
    "name": artists.name,
    "genres":artists.genres,
    "city": artists.city,
    "state": artists.state,
    "phone": artists.phone,
    "website": artists.website,
    "facebook_link": artists.facebook_link,
    "seeking_venue": artists.seeking_venue,
    "seeking_description": artists.seeking_description,
    "image_link": artists.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  alldata.insert(artists.id,respnse)
  data = list(filter(lambda d: d['id'] == artist_id, alldata))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  try:
    artist.name = request.form['name']
    artist.genres = request.form['genres']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.website = request.form['website']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_venue = request.form['seeking_venue']
    artist.seeking_description = request.form['seeking_description']
    artist.image_link = request.form['image_link']
    db.session.commit()
  except :
    db.session.rollback()
  finally:
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  
  try:
    venue.name = request.form['name']
    venue.genres = request.form['genres']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.website = request.form['website']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_venue = request.form.seeking_talent.data
    venue.seeking_description = request.form['seeking_description']
    venue.image_link = request.form['image_link']
    db.session.commit()
  except :
    db.session.rollback()
  finally:
    db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = ''
  seeking_venue= False
  form =request.form
  try:
    name = form['name']
    genres = form['genres']
    city = form['city']
    state = form['state']
    phone = form['phone']
    website = form['website']
    facebook_link = form['facebook_link']
    if "seeking_venue" in form:
      seeking_venue = form['seeking_venue']
      if seeking_venue == 'y':
        seeking_venue = True
    else:
      seeking_venue = False
    seeking_description = form['seeking_description']
    image_link = form['image_link']
    artist = Artist(name=name,genres=genres,city=city,state=state,
    phone=phone,website=website,facebook_link=facebook_link,seeking_venue=seeking_venue,
    seeking_description=seeking_description,image_link=image_link)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Show.query.all()
  for show in shows:
    data.append({ 
    "venue_id": Venue.query.get(show.venue_id).id,
    "venue_name": Venue.query.get(show.venue_id).name,
    "artist_id": Artist.query.get(show.artist_id).id,
    "artist_name": Artist.query.get(show.artist_id).name,
    "artist_image_link": Artist.query.get(show.artist_id).image_link,
    "start_time": format_datetime(show.start_time.strftime("%Y-%m-%d %H:%M:%S"))
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    venue_id = request.form['venue_id']
    artist_id = request.form['venue_id']
    start_time = request.form['start_time']
    show = Show(venue_id=venue_id,artist_id=artist_id,start_time=start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
    return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., 
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

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
