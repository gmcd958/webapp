import abc
from typing import List

from library.domain.model import Author, Book, Review, User, BooksInventory, Genre, Publisher

repo_instance = None


class RepositoryException(Exception):

    def __init__(self, message=None):
        pass


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_user(self, user: User):
        """" Adds a User to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, user_name) -> User:
        """ Returns the User named user_name from the repository.

        If there is no User with the given user_name, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_book(self, book: Book):
        """ Adds an Book to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_book(self, book_id: int) -> Book:
        """ Returns Book with id from the repository.

        If there is no Book with the given id, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_books(self) -> List[Book]:
        """ Returns Book with id from the repository.

        If there is no Book with the given id, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_books_by_release_year(self, target_year: int) -> List[Book]:
        """ Returns a list of Books that were published on target_date.

        If there are no Books on the given date, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_number_of_books(self) -> int:
        """ Returns the number of Books in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_first_book(self) -> Book:
        """ Returns the first Book, ordered by release year, from the repository.

        Returns None if the repository is empty.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_last_book(self) -> Book:
        """ Returns the last Book, ordered by release year, from the repository.

        Returns None if the repository is empty.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_books_by_id(self, id_list):
        """ Returns a list of Books, whose ids match those in id_list, from the repository.

        If there are no matches, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_book_ids_for_genre(self, genre_name: str):
        """ Returns a list of ids representing Books that are tagged by genre_name.

        If there are Books that are tagged by genre_name, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_book_ids_for_author(self, author_name: str):
        """ Returns a list of ids representing Books that are tagged by genre_name.

        If there are Books that are tagged by genre_name, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_book_ids_for_publisher(self, publisher_name: str):
        """ Returns a list of ids representing Books that are tagged by genre_name.

        If there are Books that are tagged by genre_name, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_release_year_of_previous_book(self, book: Book):
        """ Returns the date of an Book that immediately precedes book.

        If book is the first Book in the repository, this method returns None because there are no Articles
        on a previous date.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_release_year_of_next_book(self, book: Book):
        """ Returns the release_date of an Book that immediately follows book.

        If book is the last Book in the repository, this method returns None because there are no Books
        on a later date.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_genre(self, genre: Genre):
        raise NotImplementedError

    @abc.abstractmethod
    def get_genres(self) -> List[Genre]:
        raise NotImplementedError

    def add_author(self, author: Author):
        raise NotImplementedError

    # @abc.abstractmethod
    # def get_author(self, author_id: int) -> Author:
    #     """ Returns Author with id from the repository."""
    #     raise NotImplementedError

    @abc.abstractmethod
    def get_authors(self) -> List[Author]:
        raise NotImplementedError

    def add_publisher(self, publisher):
        raise NotImplementedError

    # @abc.abstractmethod
    # def get_publisher(self, publisher_id: int) -> Publisher:
    #     """ Returns Author with id from the repository."""
    #     raise NotImplementedError

    @abc.abstractmethod
    def get_publishers(self) -> List[Publisher]:
        """ Returns the Genres stored in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def add_review(self, review: Review):
        """ Adds a Reviews to the repository. """
        if review.user is None or review not in review.user.reviews:
            raise RepositoryException('Review not correctly attached to a User')
        if review.book is None or review not in review.book.reviews:
            raise RepositoryException('Review not correctly attached to an Book')

    @abc.abstractmethod
    def get_reviews(self):
        """ Returns the Reviews stored in the repository. """
        raise NotImplementedError










