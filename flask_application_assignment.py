from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

#Create App context
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'movies.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Movie model representing the movies table
class Movie(db.Model):
    __table_args__ = {'extend_existing': True}
    [...]

# Create the database and the tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def index():
    # Get all movies from the database
    movies = [...]
    return render_template('index.html', movies=movies)

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    movie = None

    if request.method ==  [...]:
        movie_id = [...]
        
        ## Handle updates here:    
        if movie_id:
            # Fetch the movie by ID if it exists
            [...]
            if movie:
                # get values for existing movie from HTML
                [...]

            else:
                return "Movie not found.", 404
        else:
            # Add new movie if no ID is provided
            movie = Movie(
                [...]
            )

        # Add and Commit changes to the database for both update and add
        [...]
        return redirect(url_for('index'))

    # Check if editing an existing movie via query parameter - pass to add values in add_movie page (optional)
    [...]
    if movie_id:
        [...]

    return render_template('add_movie.html', movie=movie)

@app.route('/delete_movie/<int:id>', methods=['POST'])
def delete_movie(id):
    # Get the movie by ID
    [...]    
    
    try:
        # Delete the movie from the database
        [...]

        return redirect(url_for('index'))
    except:
        return "There was a problem deleting that movie."

if __name__ == '__main__':
    app.run(debug=True)