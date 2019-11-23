# Imports

import babel
import dateutil.parser
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, abort
from logging import Formatter, FileHandler
from forms import ArtistForm, ShowForm, VenueForm
import re
import sys
from sqlalchemy import exc

from models import Venue, Show, Artist, app, db

# Filters


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


def validate_phone_number():
    regex = "\\w{3}-\\w{3}-\\w{4}"
    if not re.search(regex, request.form.get("phone")):
        flash('Please format the phone number XXX-XXX-XXXX')
        abort(500)


app.jinja_env.filters['datetime'] = format_datetime

# Controllers
@app.route('/')
def index():
    return render_template('pages/home.html')

#  Venues
@app.route('/venues')
def venues():
    data = Venue.query.order_by(Venue.name.asc()).all()
    city_state = db.session.query(Venue.state, Venue.city).group_by(
        Venue.state, Venue.city).order_by(Venue.state.asc(), Venue.city.asc()).all()
    return render_template('pages/venues.html', areas=data, city_state=city_state)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    search_query = Venue.query.filter(
        Venue.name.ilike("%" + search_term + "%"))
    response = {
        "count": search_query.count(),
        "data": search_query.order_by(Venue.name.asc()).all()
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # Find future shows for venue_id
    future_shows = Show.query.filter_by(venue_id=venue_id).filter(
        Show.start_time > datetime.now())

    # Find past shows for venue_id
    past_shows = Show.query.filter_by(venue_id=venue_id).filter(
        Show.start_time < datetime.now())

    response = {
        "venue": Venue.query.filter_by(id=venue_id).first(),
        "future_count": future_shows.count(),
        "future_shows": future_shows.all(),
        "past_count": past_shows.count(),
        "past_shows": past_shows.all()
    }

    return render_template('pages/show_venue.html', response=response)

#  Create Venue
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # called upon submitting the new venue listing form
    error = False
    create_venue = Venue()
    validate_phone_number()

    try:
        setattr(create_venue, 'seeking_talent', False)

        # Loop through the form results and update the venue model with the new values
        for keys, values in request.form.items():
            # Seeking_talent is a checkbox and needs special handling
            # Genres is a multi select box and needs getlist to pull all items
            if keys != 'seeking_talent' and keys != 'genres':
                setattr(create_venue, keys, values)
            if keys == 'seeking_talent':
                setattr(create_venue, keys, True)
            if keys == 'genres':
                setattr(create_venue, keys, request.form.getlist('genres'))

        # Add new form changes to session and commit
        db.session.add(create_venue)
        db.session.commit()

    except exc.IntegrityError as e:
        # There was a problem
        error = True
        db.session().rollback()
        flash('Venue ' + request.form['name'] + ' could not be created!')
        errorInfo = e.orig.args
        flash(errorInfo[0])
    except:
        # There was a problem
        error = True
        db.session.rollback()
        flash('Venue ' + request.form['name'] + ' could not be created!')
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        # show the new changes
        flash('venue ' + request.form['name'] + ' was successfully created!')
        return redirect(url_for('venues'))
    else:
        abort(500)


#  Delete Venue
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})

#  Venue - Edit (Get and Post)
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # defines the venueForm Class from forms.py
    form = VenueForm()

    # Query DB for a specific venue and populate the HTML Form
    venue = Venue.query.filter_by(id=venue_id).first()

    # Set selected values for drop down lists, multi selects, and checkboxes
    form.state.process_data(venue.state)
    form.seeking_talent.process_data(venue.seeking_talent)
    form.genres.process_data(venue.genres)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    # Check to see if the phone number is formatted correctly
    validate_phone_number()

    try:
        # Get the data model for Venue
        venue = Venue.query.filter_by(id=venue_id).first()

        # Initialize checkbox to false
        setattr(venue, 'seeking_talent', False)

        # Loop through the form results and update the venue model with the new values
        for keys, values in request.form.items():
            if keys != 'seeking_talent' and keys != 'genres':
                setattr(venue, keys, values)
            if keys == 'seeking_talent':
                setattr(venue, keys, True)
            if keys == 'genres':
                setattr(venue, keys, request.form.getlist('genres'))

        # Add venue to the session
        db.session.add(venue)

        # commit the new changes to the DB
        db.session.commit()

        # on successful db insert, flash success
        flash('venue ' + request.form['name'] + ' was successfully edited!')
    except exc.IntegrityError as e:
        # There was a problem
        error = True
        db.session().rollback()
        flash('venue ' + request.form['name'] + ' could not be created!')
        errorInfo = e.orig.args
        flash(errorInfo[0])
    except:
        # There was a problem
        error = True
        db.session.rollback()
        flash('venue ' + request.form['name'] + ' could not be created!')
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        # show the new changes
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        abort(500)

#  Artists - Show List of Artists
@app.route('/artists')
def artists():
    # Get records from artist table sort alphabetically
    data = Artist.query.order_by(Artist.name.asc()).all()
    return render_template('pages/artists.html', artists=data)

#  Artists - Search Artists by search term
@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    search_query = Artist.query.filter(
        Artist.name.ilike("%" + search_term + "%"))
    response = {
        "count": search_query.count(),
        "data": search_query.order_by(Artist.name.asc()).all()
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    # Find future shows for artist_id
    future_shows = Show.query.filter_by(artist_id=artist_id).filter(
        Show.start_time > datetime.now())

    # Find past shows for artist_id
    past_shows = Show.query.filter_by(artist_id=artist_id).filter(
        Show.start_time < datetime.now())

    response = {
        "artist": Artist.query.filter_by(id=artist_id).first(),
        "future_count": future_shows.count(),
        "future_shows": future_shows.all(),
        "past_count": past_shows.count(),
        "past_shows": past_shows.all()
    }

    return render_template('pages/show_artist.html', response=response)

#  Artists - Edit (Get and Post)
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # defines the ArtistForm Class from forms.py
    form = ArtistForm()

    # Query DB for a specific artist and populate the HTML Form
    artist = Artist.query.filter_by(id=artist_id).first()

    # Set selected values for drop down lists, multi selects, and checkboxes
    form.state.process_data(artist.state)
    form.seeking_venue.process_data(artist.seeking_venue)
    form.genres.process_data(artist.genres)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    try:
        # Check to see if the phone number is formatted correctly
        validate_phone_number()

        # Get the data model for Artist
        artist = Artist.query.filter_by(id=artist_id).first()

        # Initialize checkbox to false
        setattr(artist, 'seeking_venue', False)

        # Loop through the form results and update the artist model with the new values
        for keys, values in request.form.items():
            if keys != 'seeking_venue' and keys != 'genres':
                setattr(artist, keys, values)
            if keys == 'seeking_venue':
                setattr(artist, keys, True)
            if keys == 'genres':
                setattr(artist, keys, request.form.getlist('genres'))

            # Add artist to the session
            db.session.add(artist)

            # commit the new changes to the DB
            db.session.commit()

        # on successful db insert, flash success
        flash('artist ' + request.form['name'] + ' was successfully edited!')
    except exc.IntegrityError as e:
        # There was a problem
        error = True
        db.session().rollback()
        flash('artist ' + request.form['name'] + ' could not be created!')
        errorInfo = e.orig.args
        flash(errorInfo[0])
    except:
        # There was a problem
        error = True
        db.session.rollback()
        flash('artist ' + request.form['name'] + ' could not be created!')
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        # show the new changes
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        abort(500)

#  Create Artist (Get and Post)
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    create_artist = Artist()
    validate_phone_number()

    try:
        setattr(create_artist, 'seeking_venue', False)

        # Loop through the form results and update the artist model with the new values
        for keys, values in request.form.items():
            # seeking_venue is a checkbox and needs special handling
            # Genres is a multi select box and needs getlist to pull all items
            if keys != 'seeking_venue' and keys != 'genres':
                setattr(create_artist, keys, values)
            if keys == 'seeking_venue':
                setattr(create_artist, keys, True)
            if keys == 'genres':
                setattr(create_artist, keys, request.form.getlist('genres'))

        # Add new form changes to session and commit
        db.session.add(create_artist)
        db.session.commit()
    except exc.IntegrityError as e:
        # There was a problem
        error = True
        db.session().rollback()
        flash('Artist ' + request.form['name'] + ' could not be created!')
        errorInfo = e.orig.args
        flash(errorInfo[0])
    except:
        error = True
        db.session.rollback()
        flash('Artist ' + request.form['name'] + ' could not be created!')
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        # show the new changes
        flash('Artist ' + request.form['name'] + ' was successfully created!')
        return redirect(url_for('artists'))
    else:
        abort(500)

#  Delete Artist
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        Artist.query.filter_by(id=artist_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})

#  Shows


@app.route('/shows')
def shows():
    # Find future shows for artist_id
    future_shows = Show.query.filter(
        Show.start_time > datetime.now()).order_by(Show.start_time)

    # Find past shows for artist_id
    past_shows = Show.query.filter(
        Show.start_time < datetime.now()).order_by(Show.start_time.desc())

    response = {
        "future_count": future_shows.count(),
        "future_shows": future_shows.all(),
        "past_count": past_shows.count(),
        "past_shows": past_shows.all()
    }

    return render_template('pages/shows.html', response=response)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        create_show = Show()

        # Loop through the form results and update the show model with the new values
        for keys, values in request.form.items():
            setattr(create_show, keys, values)

        # Add new changes to session
        db.session.add(create_show)

        # commit the new changes to the DB
        db.session.commit()

        # on successful db insert, flash success
        flash('show was successfully created!')
    except:
        error = True
        db.session.rollback()
        flash('show could not be created!')
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        # show the new changes
        return redirect(url_for('shows'))
    else:
        abort(500)
    return render_template('pages/home.html')

#  Delete Show
@app.route('/shows/<show_id>', methods=['DELETE'])
def delete_show(show_id):

    try:
        Show.query.filter_by(id=show_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})


#  Shows - Edit (Get and Post)
@app.route('/shows/<int:show_id>/edit', methods=['GET'])
def edit_show(show_id):
    # Query DB for a specific show and populate the HTML Form
    show = Show.query.filter_by(id=show_id).first()

    # defines the ShowForm Class from forms.py
    form = ShowForm(request.form, obj=show)
    # form.populate_obj(show)

    return render_template('forms/edit_show.html', form=form, show=show)


@app.route('/shows/<int:show_id>/edit', methods=['POST'])
def edit_show_submission(show_id):
    # Query DB for a specific show and populate the HTML Form
    show = Show.query.filter_by(id=show_id).first()

    # Loop through the form results and update the artist model with the new values
    for keys, values in request.form.items():
        setattr(show, keys, values)

    # commit the new changes to the DN
    db.session.commit()

    # show the new changes
    return redirect(url_for('shows'))


#  Error Handlers
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


# Launch

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)'''
