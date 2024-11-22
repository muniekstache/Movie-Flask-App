from app import app, db

# Create the database and the tables
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)