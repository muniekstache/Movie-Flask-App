from flask import render_template, request, redirect, url_for, flash
from app.models import Movie, User
from app.forms import LoginForm, RegistrationForm
from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@login_required
def index():
    """
    Route: '/' + '/index'
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

                db.session.commit()
                flash('Movie updated successfully!', 'success')

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
            db.session.commit()
            flash('Movie added successfully!', 'success')

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
        flash('Movie deleted successfully!', 'success')
        return redirect(url_for('index'))
    except:
        flash('There was a problem deleting that movie.', 'danger')
        return "There was a problem deleting that movie."
