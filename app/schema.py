import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models import Movie as MovieModel, db, Genre as GenreModel
from sqlalchemy.orm import Session

class Movie(SQLAlchemyObjectType):
    class Meta:
        model = MovieModel

class Genre(SQLAlchemyObjectType):
    class Meta:
        model = GenreModel

class Query(graphene.ObjectType):
    movies = graphene.List(Movie)
    genres_by_movie = graphene.List(Genre)
    movies_by_genre = graphene.List(Movie)
    search_movies = graphene.List(Movie, title=graphene.String(), director=graphene.String(), year=graphene.Int())

    def resolve_movies(root, info):
        return db.session.execute(db.select(MovieModel)).scalars()

    def resolve_search_movies(root, info, title=None, director=None, year=None):        
        query = db.select(MovieModel)
        if title:
            query = query.where(MovieModel.title.ilike(f'%{title}%'))
        if director:
            query = query.where(MovieModel.director.ilike(f'%{director}%'))
        if year:
            query = query.where(MovieModel.year == year)
        results = db.session.execute(query).scalars().all()
        return results
    
    def resolve_movies_by_genre(root, info, id):
        query = db.select(GenreModel)
        if not id:
            return 'No movies found with that genre!'
        else:
            query = query.where(GenreModel.genre.ilike(f'%{id}%'))
    
    def resolve_movies_by_movie(root, info, id):
        query = db.select(GenreModel)
        if not id:
            return 'This genre has no movies!'
        else:
            query = query.where(MovieModel.genre.ilike(f'%{id}%'))

    

    
class AddMovie(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        director = graphene.String(required=True)
        year = graphene.Int(required=True)

    movie = graphene.Field(Movie)

    def mutate(root, info, title, director, year):
        with Session(db.engine) as session: 
            with session.begin():
                movie = MovieModel(title=title, director=director, year=year)
                session.add(movie)
            
            session.refresh(movie)
            return AddMovie(movie=movie)
        
class CreateGenre(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    genre = graphene.Field(Genre)

    def mutate(root, info, name):
        with Session(db.engine) as session:
            with session.begin():
                genre = GenreModel(name=name)
                session.add(genre)
            session.refresh(genre)
            return CreateGenre(genre=genre)

class UpdateMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        director = graphene.String()
        year = graphene.Int()

    movie = graphene.Field(Movie)

    def mutate(root, info, id, title=None, director=None, year=None):
        movie = db.session.get(MovieModel, id)         
        if not movie:
            return None
        if title:    
            movie.title = title
        if director:
            movie.director = director
        if year:
            movie.year = year
        db.session.commit()
        return UpdateMovie(movie=movie)
    
class UpdateGenre(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        movies = graphene.String()

    new_genre = graphene.Field(Genre)

    def mutate(root, info, id, name):
        genre = db.session.get(GenreModel, id)
        if not genre:
            return None
        else:
            genre.name = name
        db.session.commit()
        return UpdateGenre(genre=genre)


class DeleteMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    message = graphene.String()

    def mutate(root, info, id):
        movie = db.session.get(MovieModel, id)         
        if not movie:
            return DeleteMovie(message="That movie does not exist")
        else:
            db.session.delete(movie)
            db.session.commit()
            return DeleteMovie(message="Delete Movie")
        
class DeleteGenre(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        movies = graphene.String()

    message = graphene.String()

    def mutate(root, info, id):
        genre = db.session.get(GenreModel, id)
        if not genre:
            return DeleteGenre(message="That genre does not exist")
        else:
            db.session.delete(genre)
            db.session.commit()
            return DeleteGenre(message="Deleted Genre")

class Mutation(graphene.ObjectType):
    create_movie = AddMovie.Field()
    update_movie = UpdateMovie.Field()
    delete_movie = DeleteMovie.Field()
    create_genre = CreateGenre.Field()
    update_genre = UpdateGenre.Field()
    delete_genre = DeleteGenre.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)