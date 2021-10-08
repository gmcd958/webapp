from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, DateTime, Boolean,
    ForeignKey
)
from sqlalchemy.orm import mapper, relationship, synonym

from library.domain import model

metadata = MetaData()

users_table = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_name', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False)
)

reviews_table = Table(
    'reviews', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('users.id')),
    Column('book_id', ForeignKey('books.id')),
    Column('review_text', String(1024), nullable=False),
    Column('rating', Integer, nullable=False),
    Column('timestamp', DateTime, nullable=False)
)

publishers_table = Table(
    'publishers', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('book_id', ForeignKey('books.id')),
    Column('name', String(255), nullable=False),
)

authors_table = Table(
    'authors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('book_id', ForeignKey('books.id')),
    Column('full_name', String(255), nullable=False),
)

books_table = Table(
    'books', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False),
    Column('release_year', Integer, nullable=False),
    Column('description', String(1024), nullable=False),
    Column('imgurl', String(1024), nullable=False),
    Column('ebook', Boolean),
    Column('num_pages', Integer)
)

genres_table = Table(
    'genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('genre_name', String(255), nullable=False)
)

book_genres_table = Table(
    'book_genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('book_id', ForeignKey('books.id')),
    Column('genre_id', ForeignKey('genres.id'))
)


def map_model_to_tables():
    mapper(model.User, users_table, properties={
        '_User__user_name': users_table.c.user_name,
        '_User__password': users_table.c.password,
        '_User__reviews': relationship(model.Review, backref='_Review__user')
    })
    mapper(model.Review, reviews_table, properties={
        '_Review__review_text': reviews_table.c.review_text,
        '_Review__timestamp': reviews_table.c.timestamp
    })
    mapper(model.Publisher, publishers_table, properties={
        '_Publisher__name': publishers_table.c.name,
        '_Publisher__books': relationship(model.Book, backref='_Book__publisher')
    })
    mapper(model.Author, authors_table, properties={
        '_Author__unique_id': authors_table.c.id,
        '_Author__full_name': authors_table.c.full_name,
        '_Author__books': relationship(model.Book, backref='_Book__author')
    })
    mapper(model.Book, books_table, properties={
        '_Book__id': books_table.c.id,
        '_Book__title': books_table.c.title,
        '_Book__release_year': books_table.c.release_year,
        '_Book__description': books_table.c.description,
        '_Book__imgurl': books_table.c.imgurl,
        '_Book__ebook': books_table.c.ebook,
        '_Book__num_pages': books_table.c.num_pages,
        '_Book__reviews': relationship(model.Review, backref='_Review__book'),
        '_Book__genres': relationship(model.Genre, secondary=book_genres_table, back_populates='_Genre__genre_books')
    })
    mapper(model.Genre, genres_table, properties={
        '_Genre__genre_name': genres_table.c.genre_name,
        '_Genre__genre_books': relationship(
            model.Book,
            secondary=book_genres_table,
            back_populates="_Book__genres"
        )
    })
