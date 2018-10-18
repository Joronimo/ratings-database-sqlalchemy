"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

import correlation as c

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """provide helpful representation when printed"""

        return f"<User user_id={self.user_id} email={self.email}>"


# Put your Movie and Rating model classes here.
class Movie(db.Model):
    """Movie on ratings website."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String, nullable=False)
    released_at = db.Column(db.Date, nullable=True)
    imdb_url = db.Column(db.String, nullable=True)

    def __repr__(self):
        """provide helpful representation when printed"""

        return f"<Movie title={self.title} \
                        movie_id={self.movie_id}, \
                        released_at={self.released_at}>"

class Rating(db.Model): 
    """Movie ratings  by user"""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer, nullable=False)

    # adds an attribute that is the same as if queried user directly after
    # joining two tables
    user = db.relationship("User", backref=db.backref("ratings",
                                                      order_by=rating_id))

    movie = db.relationship("Movie", backref=db.backref("ratings",
                                                        order_by=rating_id))



    def __repr__(self):
        """provide helpful representation when printed"""

        return f"<Rating rating_id={self.rating_id}, \
                         movie_id={self.movie_id}, \
                         user_id={self.user_id}, \
                         score={self.score}>"


def judgmental_eye():
    # m = Movie.query.filter_by(title="Toy Story").first()
    u = User.query.get(956)  # person logged in

    ratings = u.ratings  # person logged in's ratings

    other_ratings = Rating.query.filter_by(movie_id=1).all()
    other_users = [r.user for r in other_ratings]  
    # list of users who have rated Toy Story

    # all the movies u has rated
    u_movie_ids = [user_rating.movie_id for user_rating in u.ratings]

    o = other_users[0]  # the first other user who has rated Toy Story

    # need a dictionary containing keys as: movie ids U/we have rated. values
    # are our rating objects of those movies.
    
    u_movies = {}
    for rating in ratings:
        u_movies[rating.movie_id] = rating.score

    # want a list of pairs where [(our score of a movie, their score of a movie)]

    pairs_list = []

    
    o_movies = db.session.query(Rating.movie_id).filter(Rating.user_id == o.user_id).all()
    o_scores = db.session.query(Rating.score).filter(Rating.user_id == o.user_id).all()
    print("USER MOVIES", o_movies)
    # Movie.query.filter_by(user_id=user.user_id).all()

    # db.session.query(Rating.score, Movie.title)
    #     .join(Movie).filter(Rating.user_id == user.user_id).all())

    # list of all movies that user has rated.
    for score in o_scores:    
        for movie in o_movies:
            if u_movies.get(movie[0]):
                pairs_list.append((u_movies.get(movie[0]), score[0]))

    






##############################################################################
# Helper functions-

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")
