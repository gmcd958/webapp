from typing import List, Iterable

from library.adapters.repository import AbstractRepository
from library.domain.model import make_review, Book, Review, Genre


class NonExistentBookException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def add_review(book_id: int, review_text: str, user_name: str, rating: int, repo: AbstractRepository):
    # Check that the article exists.
    book = repo.get_book(book_id)
    if book is None:
        raise NonExistentBookException

    user = repo.get_user(user_name)
    if user is None:
        raise UnknownUserException

    # Create comment.
    review = make_review(review_text, user, book, rating)

    # Update the repository.
    repo.add_review(review)


def get_book(book_id: int, repo: AbstractRepository):
    book = repo.get_book(book_id)

    if book is None:
        raise NonExistentBookException

    return book_to_dict(book)


def get_all_books(repo: AbstractRepository):
    books = repo.get_all_books()

    return books_to_dict(books)


def get_first_book(repo: AbstractRepository):

    book = repo.get_first_book()

    return book_to_dict(book)


def get_last_book(repo: AbstractRepository):

    book = repo.get_last_book()

    return book_to_dict(book)


def get_books_by_release_year(release_year, repo: AbstractRepository):
    # Returns articles for the target date (empty if no matches), the date of the previous article (might be null), the date of the next article (might be null)

    books = repo.get_books_by_release_year(target_year=release_year)

    books_dto = list()
    prev_year = next_year = None

    if len(books) > 0:
        prev_year = repo.get_release_year_of_previous_book(books[0])
        next_year = repo.get_release_year_of_next_book(books[0])

        # Convert Articles to dictionary form.
        books_dto = books_to_dict(books)

    return books_dto, prev_year, next_year


def get_book_ids_for_genre(genre_name, repo: AbstractRepository):
    book_ids = repo.get_book_ids_for_genre(genre_name)

    return book_ids


def get_book_ids_for_author(author_name, repo: AbstractRepository):
    book_ids = repo.get_book_ids_for_author(author_name)

    return book_ids


def get_book_ids_for_publisher(publisher_name, repo: AbstractRepository):
    book_ids = repo.get_book_ids_for_publisher(publisher_name)

    return book_ids


def get_books_by_id(id_list, repo: AbstractRepository):
    books = repo.get_books_by_id(id_list)

    # Convert Books to dictionary form.
    books_as_dict = books_to_dict(books)

    return books_as_dict


def get_reviews_for_book(book_id, repo: AbstractRepository):
    book = repo.get_book(book_id)

    if book is None:
        raise NonExistentBookException

    return reviews_to_dict(book.reviews)


# ============================================
# Functions to convert model entities to dicts
# ============================================

def book_to_dict(book: Book):
    book_dict = {
        'book_id': book.book_id,
        'release_year': book.release_year,
        'title': book.title,
        'author_id': book.author,
        'description': book.description,
        'imgurl': book.imgurl,
        'reviews': reviews_to_dict(book.reviews),
        'genres': genres_to_dict(book.genres)
    }
    return book_dict


def books_to_dict(books: Iterable[Book]):
    return [book_to_dict(book) for book in books]


def review_to_dict(review: Review):
    review_dict = {
        'book_id': review.book.book_id,
        'review_text': review.review_text,
        'user_name': review.user,
        'rating': review.rating,
    }
    return review_dict


def reviews_to_dict(reviews: Iterable[Review]):
    return [review_to_dict(review) for review in reviews]


def genre_to_dict(genre: Genre):
    genre_dict = {
        'genre_name': genre.genre_name,
        'genre_books': [book.book_id for book in genre.genre_books]
    }
    return genre_dict


def genres_to_dict(genres: Iterable[Genre]):
    return [genre_to_dict(genre) for genre in genres]


# ============================================
# Functions to convert dicts to model entities
# ============================================

def dict_to_book(dict):
    book = Book(dict.book_id, dict.release_year, dict.book_title)
    book.author = dict.author_id
    book.description = dict.description
    book.imgurl = dict.imgurl

    # Note there's no comments or tags.
    return book
