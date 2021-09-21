from typing import Iterable
import random

from library.adapters.repository import AbstractRepository
from library.domain.model import Book


def get_genre_names(repo: AbstractRepository):
    genres = repo.get_genres()
    genre_names = [genre.genre_name for genre in genres]

    return genre_names


def get_random_books(quantity, repo: AbstractRepository):
    book_count = repo.get_number_of_books()

    if quantity >= book_count:
        # Reduce the quantity of ids to generate if the repository has an insufficient number of articles.
        quantity = book_count - 1

    # Pick distinct and random articles.
    random_ids = random.sample(range(1, book_count), quantity)
    books = repo.get_books_by_id(random_ids)

    return books_to_dict(books)


# ============================================
# Functions to convert dicts to model entities
# ============================================

def book_to_dict(book: Book):
    book_dict = {
        'book_id': book.book_id,
        'release_year': book.release_year,
        'title': book.title,
        'author_id': book.author,
        'description': book.description,
        'imgurl': book.imgurl,
    }
    return book_dict


def books_to_dict(books: Iterable[Book]):
    return [book_to_dict(book) for book in books]
