from flask import render_template, request, redirect, url_for
from app.models import Movie
from app import app, db

@app.route('/', methods=['GET'])
def index():
    """
    Route: '/'
    Methods: GET
    Purpose: Display all movies.
    Reasoning:
        - Uses GET to safely retrieve data without modifying server state.
    """
    # Get all movies from the database
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)


@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    """
    Route: '/add_movie'
    Methods: GET, POST
    Purpose: Add a new movie or edit an existing one.
    Reasoning:
        - GET to display the form for adding/editing.
        - POST to submit form data and modify the database.
    """
    movie = None

    if request.method == 'POST':
        movie_id = request.form.get('id')

        ## Handle updates here:
        if movie_id:
            # Fetch the movie by ID if it exists
            movie = Movie.query.get(movie_id)
            if movie:
                # get values for existing movie from HTML
                movie.name = request.form['name']
                movie.year = request.form['year']
                movie.oscars = request.form['oscars']

            else:
                return "Movie not found.", 404
        else:
            # Add new movie if no ID is provided
            movie = Movie(
                name=request.form['name'],
                year=request.form['year'],
                oscars=request.form['oscars']
            )
            db.session.add(movie)

        # Add and Commit changes to the database for both update and add
        db.session.commit()
        return redirect(url_for('index'))

    # Check if editing an existing movie via query parameter - pass to add values in add_movie page (optional)
    movie_id = request.args.get('id')
    if movie_id:
        movie = Movie.query.get(movie_id)

    return render_template('add_movie.html', movie=movie)


@app.route('/delete_movie/<int:id>', methods=['POST'])
def delete_movie(id):
    """
    Route: '/delete_movie/<int:id>'
    Methods: POST
    Purpose: Delete a movie by ID.
    Reasoning:
        - POST is used to modify server state by deleting data.
        - HTML forms don't support DELETE, so POST is used.
    """
    # Get the movie by ID
    movie = Movie.query.get_or_404(id)

    try:
        # Delete the movie from the database
        db.session.delete(movie)
        db.session.commit()
        return redirect(url_for('index'))
    except:
        return "There was a problem deleting that movie."
