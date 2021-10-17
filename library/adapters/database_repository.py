from datetime import date
from typing import List

from sqlalchemy import desc, asc
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from sqlalchemy.orm import scoped_session
from flask import _app_ctx_stack

# from covid.domain.model import User, Article, Comment, Tag

from library.domain.model import Publisher, Author, Book, Review, User, Genre
from library.adapters.repository import AbstractRepository


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def close_current_session(self):
        if not self.__session is None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    def add_user(self, user: User):
        with self._session_cm as scm:
            scm.session.add(user)
            scm.commit()

    def get_user(self, user_name: str) -> User:
        user = None
        try:
            user = self._session_cm.session.query(User).filter(User._User__user_name == user_name).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return user

    def add_book(self, book: Book):
        with self._session_cm as scm:
            scm.session.add(book)
            scm.commit()

    def get_book(self, id: int) -> Book:
        book = None
        try:
            book = self._session_cm.session.query(Book).filter(Book._Book__book_id == id).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return book

    def get_all_books(self) -> List[Book]:
        books = self._session_cm.session.query(Book).all()
        return books

    def get_books_by_release_year(self, target_year) -> List[Book]:
        if target_year is None:
            books = self._session_cm.session.query(Book).all()
            return books
        else:
            # Return articles matching target_date; return an empty list if there are no matches.
            books = self._session_cm.session.query(Book).filter(Book._Book__release_year == target_year).all()
            return books

    def get_number_of_books(self):
        number_of_books = self._session_cm.session.query(Book).count()
        return number_of_books

    def get_first_book(self):
        book = self._session_cm.session.query(Book).first()
        return book

    def get_last_book(self):
        book = self._session_cm.session.query(Book).order_by(desc(Book._Book__book_id)).first()
        return book

    def get_books_by_id(self, id_list: List[int]):
        books = self._session_cm.session.query(Book).filter(Book._Book__book_id.in_(id_list)).all()
        return books

    def get_book_ids_for_genre(self, genre_name: str):
        book_ids = []

        # Use native SQL to retrieve article ids, since there is no mapped class for the article_tags table.
        row = self._session_cm.session.execute('SELECT id FROM genres WHERE genre_name = :genre_name', {'genre_name': genre_name}).fetchone()

        if row is None:
            # No tag with the name tag_name - create an empty list.
            book_ids = list()
        else:
            genre_id = row[0]
            # Retrieve article ids of articles associated with the tag.
            book_ids = self._session_cm.session.execute(
                    'SELECT book_id FROM book_genres WHERE genre_id = :genre_id ORDER BY genre_id ASC',
                    {'genre_id': genre_id}
            ).fetchall()
            book_ids = [id[0] for id in book_ids]

        return book_ids

    def get_book_ids_for_author(self, author_name: str):
        book_ids = []

        # Use native SQL to retrieve article ids, since there is no mapped class for the article_tags table.
        row = self._session_cm.session.execute('SELECT id FROM authors WHERE authors.full_name = :authors.full_name', {'authors.full_name': author_name}).fetchone()

        if row is None:
            # No tag with the name tag_name - create an empty list.
            book_ids = list()
        else:
            author_id = row[0]
            # Retrieve article ids of articles associated with the tag.
            book_ids = self._session_cm.session.execute(
                    'SELECT books.id FROM authors WHERE author.id = :author.id ORDER BY author.id ASC',
                    {'author.id': author_id}
            ).fetchall()
            book_ids = [id[0] for id in book_ids]

        return book_ids

    def get_book_ids_for_publisher(self, publisher_name: str):
        book_ids = []

        # Use native SQL to retrieve article ids, since there is no mapped class for the article_tags table.
        row = self._session_cm.session.execute('SELECT id FROM publishers WHERE publishers.name = :publishers.name', {'publishers.name': publisher_name}).fetchone()

        if row is None:
            # No tag with the name tag_name - create an empty list.
            book_ids = list()
        else:
            publisher_id = row[0]
            # Retrieve article ids of articles associated with the tag.
            book_ids = self._session_cm.session.execute(
                    'SELECT books.id FROM publishers WHERE publisher.id = :publisher.id ORDER BY publisher.id ASC',
                    {'publisher_id': publisher_id}
            ).fetchall()
            book_ids = [id[0] for id in book_ids]

        return book_ids

    def get_release_year_of_previous_book(self, book: Book):
        result = None
        prev_book = self._session_cm.session.query(Book).filter(Book._Book__release_year < book.release_year).order_by(desc(Book._Book__release_year)).first()

        if prev_book is not None:
            result = prev_book.release_year

        return result

    def get_release_year_of_next_book(self, book: Book):
        result = None
        next_book = self._session_cm.session.query(Book).filter(Book._Book__release_year > book.release_year).order_by(asc(Book._Book__release_year)).first()

        if next_book is not None:
            result = next_book.release_year

        return result

    def add_author(self, author: Author):
        with self._session_cm as scm:
            scm.session.add(author)
            scm.commit()

    def get_authors(self) -> List[Author]:
        authors = self._session_cm.session.query(Author).all()
        return authors

    def add_publisher(self, publisher: Publisher):
        with self._session_cm as scm:
            scm.session.add(publisher)
            scm.commit()

    def get_publishers(self) -> List[Publisher]:
        publishers = self._session_cm.session.query(Publisher).all()
        return publishers

    def add_genre(self, genre: Genre):
        with self._session_cm as scm:
            scm.session.add(genre)
            scm.commit()

    def get_genres(self) -> List[Genre]:
        genres = self._session_cm.session.query(Genre).all()
        return genres

    def add_review(self, review: Review):
        super().add_review(review)
        with self._session_cm as scm:
            scm.session.add(review)
            scm.commit()

    def get_reviews(self) -> List[Review]:
        reviews = self._session_cm.session.query(Review).all()
        return reviews