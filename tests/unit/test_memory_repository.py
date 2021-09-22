from datetime import date, datetime
from typing import List

import pytest

from library.domain.model import make_review, Book, Review, Genre, User, Author
from library.adapters.repository import RepositoryException


def test_repository_can_add_a_user(in_memory_repo):
    user = User('dave', '123456789')
    in_memory_repo.add_user(user)

    assert in_memory_repo.get_user('dave') is user


def test_repository_can_retrieve_a_user(in_memory_repo):
    user = in_memory_repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')


def test_repository_does_not_retrieve_a_non_existent_user(in_memory_repo):
    user = in_memory_repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_book_count(in_memory_repo):
    number_of_books = in_memory_repo.get_number_of_books()

    # Check that the query returned 6 Books.
    assert number_of_books == 4


def test_repository_can_add_book(in_memory_repo):
    book = Book(
        1993,
        'It was revealed ...',
        4
    )
    in_memory_repo.add_book(book)

    assert in_memory_repo.get_book(4) is book


def test_repository_can_retrieve_book(in_memory_repo):
    book = in_memory_repo.get_book(1)

    # Check that the Book has the expected title.
    assert book.title == 'The House of Memory'

    # Check that the Book is reviewed as expected.
    review_one = [review for review in book.reviews if review.review_text == "I haven't read a fun mystery book in a while and not sure I've ever read Crowner Royal. Was looking for a fun read set in France while I was on holiday there and this didn't disappoint!"][0]

    assert review_one.user.user_name == 'thorke'

    # Check that the Book is genre as expected.
    assert book.is_genred_by(Genre('Crime'))


def test_repository_does_not_retrieve_a_non_existent_book(in_memory_repo):
    book = in_memory_repo.get_book(101)
    assert book is None


def test_repository_can_retrieve_books_by_date(in_memory_repo):
    books = in_memory_repo.get_books_by_release_year(2003)

    # Check that the query returned 1 Books.
    assert len(books) == 2


def test_repository_does_not_retrieve_an_book_when_there_are_no_books_for_a_given_date(in_memory_repo):
    books = in_memory_repo.get_books_by_release_year(2000)
    assert len(books) == 0


def test_repository_can_retrieve_genres(in_memory_repo):
    genres: List[Genre] = in_memory_repo.get_genres()

    assert len(genres) == 3

    genre_one = [genre for genre in genres if genre.genre_name == 'Mystery'][0]
    genre_two = [genre for genre in genres if genre.genre_name == 'Crime'][0]
    genre_three = [genre for genre in genres if genre.genre_name == 'Thriller'][0]

    assert genre_one.number_of_genre_books == 2
    assert genre_two.number_of_genre_books == 3
    assert genre_three.number_of_genre_books == 2


def test_repository_can_get_first_book(in_memory_repo):
    book = in_memory_repo.get_first_book()
    assert book.title == 'The House of Memory'


def test_repository_can_get_last_book(in_memory_repo):
    book = in_memory_repo.get_last_book()
    assert book.title == 'Crowner Royal'


def test_repository_can_get_books_by_ids(in_memory_repo):
    books = in_memory_repo.get_books_by_id([1, 2, 3])

    assert len(books) == 3
    assert books[0].title == 'The House of Memory'
    assert books[1].title == "Toxin"
    assert books[2].title == 'A Murder is Announced'


def test_repository_does_not_retrieve_book_for_non_existent_id(in_memory_repo):
    books = in_memory_repo.get_books_by_id([1, 100])

    assert len(books) == 1
    assert books[0].title == 'The House of Memory'


def test_repository_returns_an_empty_list_for_non_existent_ids(in_memory_repo):
    books = in_memory_repo.get_books_by_id([0, 9])

    assert len(books) == 0


def test_repository_returns_book_ids_for_existing_genre(in_memory_repo):
    book_ids = in_memory_repo.get_book_ids_for_genre('Crime')

    assert book_ids == [1, 3, 4]


def test_repository_returns_an_empty_list_for_non_existent_genre(in_memory_repo):
    book_ids = in_memory_repo.get_book_ids_for_genre('United States')

    assert len(book_ids) == 0


def test_repository_returns_date_of_previous_book(in_memory_repo):
    book = in_memory_repo.get_book(3)
    print(book.release_year)
    previous_date = in_memory_repo.get_release_year_of_previous_book(book)

    assert previous_date == 1987


def test_repository_returns_none_when_there_are_no_previous_books(in_memory_repo):
    book = in_memory_repo.get_book(1)
    previous_date = in_memory_repo.get_release_year_of_previous_book(book)

    assert previous_date is None


def test_repository_returns_date_of_next_book(in_memory_repo):
    book = in_memory_repo.get_book(2)
    next_date = in_memory_repo.get_release_year_of_next_book(book)

    assert next_date == 2009


def test_repository_returns_none_when_there_are_no_subsequent_books(in_memory_repo):
    book = in_memory_repo.get_book(4)
    next_date = in_memory_repo.get_release_year_of_next_book(book)

    assert next_date is None


def test_repository_can_add_a_genre(in_memory_repo):
    genre = Genre('Horror')
    in_memory_repo.add_genre(genre)

    assert genre in in_memory_repo.get_genres()


def test_repository_can_add_a_review(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    book = in_memory_repo.get_book(2)
    review = make_review("Trump's onto it!", user, book, 5)

    in_memory_repo.add_review(review)

    assert review in in_memory_repo.get_reviews()


def test_repository_does_not_add_a_review_without_a_user(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    book = in_memory_repo.get_book(2)
    review = Review(book, "Trump's onto it!", user, 5)

    with pytest.raises(RepositoryException):
        in_memory_repo.add_review(review)


def test_repository_does_not_add_a_review_without_an_book_properly_attached(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    book = in_memory_repo.get_book(2)
    review = Review(book, "Trump's onto it!", user, 5)

    user.add_review(review)

    with pytest.raises(RepositoryException):
        # Exception expected because the Book doesn't refer to the Review.
        in_memory_repo.add_review(review)


def test_repository_can_retrieve_reviews(in_memory_repo):
    assert len(in_memory_repo.get_reviews()) == 1



