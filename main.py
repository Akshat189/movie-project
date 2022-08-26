from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

API_KEY = "f3f3a7f3d7294a72f0cb8545b2f7b1ea"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False, unique=True)
    description = db.Column(db.String(250), nullable=False, unique=False)
    rating = db.Column(db.Float, nullable=True, unique=False)
    ranking = db.Column(db.Integer, nullable=True, unique=False)
    review = db.Column(db.String(250), nullable=True, unique=False)
    img_url = db.Column(db.String(250), nullable=False)
db.create_all()

# db.session.add(
#     Movie(
#         title="Phone Booth",
#         year=2002,
#         description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#         rating=7.3,
#         ranking=10,
#         review="My favourite character was the caller.",
#         img_url="https://th.bing.com/th/id/OIP.CK3Aun-HcdmbNdOukavDHwHaLH?w=182&h=273&c=7&r=0&o=5&dpr=1.25&pid=1.7"
#     )
# )
# db.session.commit()

class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 is e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")

@app.route("/edit", methods=["GET", "POST"])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form, movie_id=movie_id)

@app.route("/delete", methods=["GET", "POST"])
def delete():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

class AddMovieForm(FlaskForm):
    title = StringField("Movie Title")
    submit = SubmitField("Add Movie")

@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddMovieForm()

    if form.validate_on_submit():
        movie_name = form.title.data
        response = requests.get("https://api.themoviedb.org/3/search/movie?api_key=f3f3a7f3d7294a72f0cb8545b2f7b1ea", params={"query": movie_name})
        data = response.json()['results']
        print(data)

        return render_template("select.html", options = data)

    return render_template("add.html", form=form)
#
# @app.route("/select", methods=["GET", "POST"])
# def select():
#     if request.method == "GET":
#         movie_name = request.args.get("title")
#         response = requests.get("https://api.themoviedb.org/3/movie/550?api_key=f3f3a7f3d7294a72f0cb8545b2f7b1ea",  params={"query": movie_name})
#         data = response.json()["results"]

@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"https://api.themoviedb.org/3/movie/{movie_api_id}"
        response = requests.get(movie_api_url, params={"api_key": "f3f3a7f3d7294a72f0cb8545b2f7b1ea", "language": "en-US"})
        data = response.json()
        print(data)
        new_movie = Movie(
            title=data["original_title"],
            # The data in release_date includes month and day, we will want to get rid of.
            year=data["release_date"].split("-")[0],
            img_url=f"https://image.tmdb.org/t/p/w500/{data['poster_path']}",
            description=data["overview"],
            rating = 7.3,
            ranking= 10,
            review="My favourite character was the caller.",
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('rate_movie',id= new_movie.id))





@app.route("/")
def home():
    all_movies = Movie.query.all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


if __name__ == '__main__':
    app.run(debug=True)
