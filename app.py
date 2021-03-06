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
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='Venue', lazy=True)

    def venue_pay_load(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'image_link': self.image_link,
        }


class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean)
  seeking_description = db.Column(db.String(500))
  website = db.Column(db.String(500))
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String))
  shows = db.relationship('Show', backref='Artist', lazy=True)

  def artist_pay_load(self):
    return {
        'id': self.id,
        'name': self.name,
        'genres': self.genres,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'facebook_link': self.facebook_link,
        'image_link': self.image_link,
        'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description,
        'website': self.website
    }

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id))
  artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id))
  show_time = db.Column(db.DateTime, nullable=False)
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
  def find(lst, key1, value1, key2, value2):
    for (i, dic) in enumerate(lst):
        if dic[key1] == value1 and dic[key2] == value2:
            return {"success": True, "index": i}
    return {"success": False, "index": -1}

  venues = Venue.query.group_by(Venue.id, Venue.city, Venue.state).all()
  data = []
  a = 0;
  for venue in venues:
      findVal = find(data, 'city', venue.city, 'state', venue.state)
      if (findVal['success']):
        data_dic = data[findVal['index']]['venues']
        data_dic.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(data_dic) + 1
        })
      else:
        data.append({
            'city': venue.city,
            'state': venue.state,
            'venues': [{
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": 1
            }]
        })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  # print(search_term)
  venues = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  response = {
    "count" : len(venues),
    "data": venues
  }
  print(response)
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  venue_pay_load = Venue.venue_pay_load(venue)
  venue_pay_load['past_shows'] = []
  venue_pay_load['upcoming_shows'] = []
  shows = Show.query.filter(Show.venue_id == venue_id).all()
  current_time = datetime.now()
  upcoming_show_count = 0
  past_show_count = 0
  for show in shows:
    if show.show_time >= current_time:
      venue_pay_load['upcoming_shows'].append(show)
      upcoming_show_count +=1
    else:
      venue_pay_load['past_shows'].append(show)
      past_show_count += 1
  venue_pay_load['upcoming_show_count'] = upcoming_show_count
  venue_pay_load['past_show_count'] = past_show_count
  return render_template('pages/show_venue.html', venue=venue_pay_load)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form=VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  print('request.form' + request.form['name'],)
  name = request.form['name']
  try:
    venue = Venue(
        name=request.form['name'],
        genres=request.form.getlist('genres'),
        address=request.form['address'],
        city=request.form['city'],
        state=request.form['state'],
        phone=request.form['phone'],
        facebook_link=request.form['facebook_link'],
        seeking_talent=False,
        seeking_description=''
    )
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except :
    db.session.rollback()
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except :
    db.session().rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  data = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  response={
      "count": len(data),
      "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id

  artist = Artist.query.get(artist_id)
  artist_pay_load = Artist.artist_pay_load(artist)
  artist_pay_load['genres'] = (
      [] if artist_pay_load['genres'] == None else artist_pay_load['genres'])
  artist_pay_load['past_shows'] = []
  artist_pay_load['upcoming_shows'] = []
  shows = Show.query.filter(Show.artist_id == artist_id).all()
  current_time = datetime.now()
  upcoming_show_count = 0
  past_show_count = 0
  for show in shows:
    if show.show_time >= current_time:
      artist_pay_load['upcoming_shows'].append(show)
      upcoming_show_count += 1
    else:
      artist_pay_load['past_shows'].append(show)
      past_show_count += 1
  artist_pay_load['upcoming_show_count'] = upcoming_show_count
  artist_pay_load['past_show_count'] = past_show_count

  return render_template('pages/show_artist.html', artist=artist_pay_load)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form=ArtistForm()
  artist = Artist.query.get(artist_id)
  
  form.name.data = artist["name"]
  form.genres.data = artist["genres"]
  form.city.data = artist["city"]
  form.state.data = artist["state"]
  form.phone.data = artist["phone"]
  form.website.data = artist["website"]
  form.facebook_link.data = artist["facebook_link"]
  form.seeking_venue.data = artist["seeking_venue"]
  form.seeking_description.data = artist["seeking_description"]
  form.image_link.data = artist["image_link"]
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  artist = Artist.query.get(artist_id)
  artist.name=request.form['name'],
  artist.genres=request.form.getlist('genres'),
  artist.address=request.form['address'],
  artist.city=request.form['city'],
  artist.state=request.form['state'],
  artist.phone=request.form['phone'],
  artist.facebook_link=request.form['facebook_link']
    
  db.session.add(artist)
  db.session.commit()
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form=VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue["name"]
  form.genres.data = artist["genres"]
  form.city.data = artist["city"]
  form.state.data = artist["state"]
  form.phone.data = artist["phone"]
  form.facebook_link.data = artist["facebook_link"]
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  venue.name=request.form['name'],
  venue.genres=request.form.getlist('genres'),
  venue.address=request.form['address'],
  venue.city=request.form['city'],
  venue.state=request.form['state'],
  venue.phone=request.form['phone'],
  venue.facebook_link=request.form['facebook_link']
  db.session.add(venue)
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form=ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  try:
    artist = Artist(
        name=request.form['name'],
        city=request.form['city'],
        state=request.form['state'],
        address=request.form['address'],
        phone=request.form['phone'],
        genres=request.form['genres'],
        facebook_link=request.form['facebook_link']
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except expression as identifier:
    flash('An error occurred. Artist ' +
          request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  # on successful db insert, flash success
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Show.query.options(db.joinedload(
      Show.Venue), db.joinedload(Show.Artist)).all()
  
  return render_template('pages/shows.html', shows=shows)

@app.route('/`shows/create`')
def create_shows():
  # renders form. do not touch.
  form=ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  try:
    show = Show(
        venue_id=request.form['venue_id'],
        artist_id=request.form['artist_id'],
        start_time=request.form['start_time'],
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except :
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

      
# on successful db insert, flash success

# e.g., flash('An error occurred. Show could not be listed.')
# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler=FileHandler('error.log')
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

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
