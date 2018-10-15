"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User
from model import Rating
from model import Movie

from model import connect_to_db, db
from server import app
from datetime import datetime


def load_users():
    """Load users from u.user into database."""

    print("Users")

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()

    print(User.query.all())


def load_movies():
    """Load movies from u.item into database."""

    print("Movies")

    Movie.query.delete()

    for row in open("seed_data/u.item"):
        row = row.rstrip()
        movie_id, title, released_at, video_released_date, imdb_url, \
            unknown, Action, Adventure, Animation, Children, Comedy, \
            Crime, Documentary, Drama, Fantasy, FilmNoir, Horror, Musical, \
            Mystery, Romance, SciFi, Thriller, War, Western = row.split("|")

        title_formatted = title[:-7]

        if released_at:
            released_at_formatted = datetime.strptime(released_at, '%d-%b-%Y')           
        else:
            released_at_formatted = None

        movie = Movie(movie_id=movie_id,
                      title=title_formatted,
                      released_at=released_at_formatted,
                      imdb_url=imdb_url)

        db.session.add(movie)

    db.session.commit()

    print(Movie.query.all())



def load_ratings():
    """Load ratings from u.data into database."""

    print("Ratings")

    Rating.query.delete()

    for row in open("seed_data/u.data"):
        row = row.rstrip()
        user_id, movie_id, score, timestamp = row.split("\t")

        rating = Rating(movie_id=movie_id,
                        user_id=user_id,
                        score=score)

        db.session.add(rating)

    db.session.commit()

    print(Rating.query.all())



def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
    # set_val_user_id()
