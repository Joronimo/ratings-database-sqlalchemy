"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session,
                   Markup)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie

# from seed import *


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    logout = request.args.get("loggedOut")

    if logout:
        session.clear()
        message = Markup("You have been successfully logged out.")
        flash(message)


    return render_template("homepage.html")

@app.route("/users")
def lists_all_users():
    """Show list of all users"""

    users = User.query.all()
    return render_template("list_all_users.html", users=users)

@app.route("/registration")
def registration():
    """Show registration page to enter email and password."""

    return render_template("registration.html")

@app.route("/process-registration", methods=["POST"])
def processed_registration():

    email = request.form.get("email")
    password = request.form.get("password")

    email_users = db.session.query(User.email)
    emails = email_users.filter(User.email == email).all()

    print("LOOK FOR THIS!!!!", emails)

    if emails == []:
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.user_id
        message = Markup("You are now registered!")
        flash(message)
        return render_template("homepage.html")
    else:
        message = Markup("You already have an account. Please log in.")
        flash(message)
        return render_template("login.html")


@app.route("/login")
def login():
    """Show login page to enter email and password."""

    return render_template("login.html")

@app.route("/process-login", methods=["POST"])
def processed_login():

    email = request.form.get("email")
    password = request.form.get("password")

    emails = db.session.query(User.email).filter(User.email == email).all()

    for tup in emails:
        if email in tup:
            user_id = db.session.query(User.user_id).filter(User.email == email).all()
            user_id = user_id[0][0]
            session["user_id"] = user_id
            message = Markup("Logged In")
            flash(message)
            return redirect(f"/users/{user_id}")

    message = Markup("This email is not registered. Please register here.")
    flash(message)
    return render_template("registration.html")


@app.route("/users/<int:user_id>")
def show_user_info(user_id):
    """from URL with user ID, get all user information and display user page"""

    users = User.query.all()

    for user in users:
        if user.user_id == user_id:

            # user_ratings = Rating.query.filter(Rating.user_id == user.user_id).all()

            movie_and_rating_id = (
            db.session.query(Rating.score, Movie.title)
            .join(Movie).filter(Rating.user_id == user.user_id).all())

            return render_template("user_info.html",
                                   user=user,
                                   movies_and_ratings=movie_and_rating_id)


@app.route("/movies")
def show_all_movies():

    movies = Movie.query.order_by(Movie.title).all()

    return render_template("list_all_movies.html", movies=movies)

@app.route("/movies/<int:movie_id>")
def show_movie_info(movie_id):
    """from URL with movie ID, get all movie information and display movie page"""

    movie = Movie.query.filter_by(movie_id=movie_id).first()

    list_of_ratings = Rating.query.filter_by(movie_id=movie_id)

    users = []
    scores = []

    for rating in list_of_ratings:
        users.append(rating.user.user_id)
        scores.append(rating.score)

    users_and_scores = zip(users, scores)

    return render_template("movie_info.html", movie=movie,
                           users_and_scores=users_and_scores)

@app.route("/add-rating", methods=["POST"])
def add_a_rating():
    """Add a rating to a movie."""

    if not session["user_id"]:
        return redirect("/login")
    else:
        movie_id = request.form.get("movie_id")
        rating = request.form.get("score")
        user_id = session["user_id"]

        user_movie_rating = Rating.query.filter_by(movie_id=movie_id, user_id=user_id).first()

        if user_movie_rating:
            message = Markup("You have already rated this movie. \
                This has updated your previous rating.")
            flash(message)

            user_movie_rating.score = rating

            db.session.add(user_movie_rating)

            db.session.commit()

            return redirect("/movies")

        else:
            new_rating = Rating(user_id=user_id, movie_id=movie_id, score=rating)

            db.session.add(new_rating)

            db.session.commit()
            message = Markup("Your rating has been successfully added!")
            flash(message)
            return redirect("/movies")
       








if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
