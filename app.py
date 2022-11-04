from flask import Flask, request
from flask.views import View
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

from create_data import director, genre, movie

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

api = Api(app)

director_ns = api.namespace("directors")
genres_ns = api.namespace("genres")
movies_ns = api.namespace("movies")


# Вьшка с отображением фильмов с учетом возможной фильтрации по режиссеру и(или) жанру
@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        all_movies = db.session.query(Movie)

        director_id = request.args.get('director_id')
        if director_id:
            all_movies = all_movies.filter(Movie.director_id == director_id)

        genre_id = request.args.get('genre_id')
        if genre_id:
            all_movies = all_movies.filter(Movie.genre_id == genre_id)

        return movies_schema.dump(all_movies), 200

    # Добавление нового фильма
    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)

        with db.session.begin():
            db.session.add(new_movie)

        return "", 201


@movies_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid):
        try:
            movie = db.session.query(Movie).get(uid)
            return movie_schema.dump(movie)
        except Exception as e:
            return str(e), 404

    def put(self, uid):
        movie = db.session.query(Movie).get(uid)
        req_json = request.json

        movie.title = req_json.get('title')
        movie.description = req_json.get('description')
        movie.trailer = req_json.get('trailer')
        movie.year = req_json.get('year')
        movie.rating = req_json.get('rating')
        movie.genre_id = req_json.get('genre_id')
        movie.director_id = req_json.get('director_id')

        db.session.add(movie)
        db.session.commit()

        return "", 204

    def patch(self, uid):
        movie = db.session.query(Movie).get(uid)
        req_json = request.json

        if "name" in req_json:
            movie.name = req_json.get('name')
        if "description" in req_json:
            movie.description = req_json.get('description')
        if "trailer" in req_json:
            movie.trailer = req_json.get('trailer')
        if "year" in req_json:
            movie.year = req_json.get('year')
        if "rating" in req_json:
            movie.rating = req_json.get('rating')
        if "genre_id" in req_json:
            movie.genre_id = req_json.get('genre_id')
        if "director_id" in req_json:
            movie.director_id = req_json.get('director_id')

        db.session.add(movie)
        db.session.commit()

        return "", 204

    def delete(self, uid):
        movie = db.session.query(Movie).get(uid)
        db.session.delete(movie)
        db.session.commit()

        return "", 204


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        directors = db.session.query(Director)
        return directors_schema.dump(directors), 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)

        with db.session.begin():
            db.session.add(new_director)

        return "", 201


@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid):
        try:
            director = db.session.query(Director).get(uid)
            return director_schema.dump(director)
        except Exception as e:
            return str(e), 404

    def put(self, uid):
        director = db.session.query(Director).get(uid)
        req_json = request.json
        if director is None:
            return "", 404
        director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()

        return "", 204

    def delete(self, uid):
        director = db.session.query(Director).get(uid)
        db.session.delete(director)
        db.session.commit()
        return "", 204


@genres_ns.route('/')
class GenresView(Resource):
    def get(self):
        genres = db.session.query(Genre).all()
        return genres_schema.dump(genres), 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)

        with db.session.begin():
            db.session.add(new_genre)
            db.session.commit()

        return "", 201


@genres_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid):
        try:
            genre = db.session.query(Genre).get(uid)
            return genre_schema.dump(genre)
        except Exception as e:
            return str(e), 404

    def put(self, uid):
        genre = db.session.query(Genre).get(uid)
        req_json = request.json
        if genre is None:
            return "", 404
        genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()

        return "", 204

    def delete(self, uid):
        genre = db.session.query(Genre).get(uid)
        db.session.delete(genre)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
