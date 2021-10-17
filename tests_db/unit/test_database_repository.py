from datetime import date, datetime

import pytest

import library.adapters.repository as repo
from library.adapters.database_repository import SqlAlchemyRepository
from library.domain.model import User, Book, Genre, Review, make_review
from library.adapters.repository import RepositoryException


def test_repository_can_add_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = User('Dave', '123456789')
    repo.add_user(user)

    repo.add_user(User('Martin', '123456789'))

    user2 = repo.get_user('Dave')

    assert user2 == user and user2 is user


def test_repository_can_retrieve_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')


def test_repository_does_not_retrieve_a_non_existent_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_book_count(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_books = repo.get_number_of_books()

    # Check that the query returned 20 Books.
    assert number_of_books == 20


def test_repository_can_add_book(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_books = repo.get_number_of_books()

    new_book_id = number_of_books + 1

    book = Book(
        1923,
        'The War',
        new_book_id
    )
    repo.add_book(book)

    assert repo.get_book(new_book_id) == book


def test_repository_can_retrieve_book(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book = repo.get_book(1)

    # Check that the Book has the expected title.
    assert book.title == 'Coronavirus: First case of virus in New Zealand'

    # Check that the Book is reviewed as expected.
    review_one = [review for review in book.reviews if review.review_text == 'Oh no, COVID-19 has hit New Zealand'][0]
    review_two = [review for review in book.reviews if review.review_text == 'Yeah Freddie, bad news'][0]

    assert review_one.user.user_name == 'fmercury'
    assert review_two.user.user_name == "thorke"

    # Check that the Book is genre as expected.
    assert book.is_genred_by(Genre('Health'))
    assert book.is_genred_by(Genre('New Zealand'))


def test_repository_does_not_retrieve_a_non_existent_book(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book = repo.get_book(201)
    assert book is None


def test_repository_can_retrieve_books_by_date(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    books = repo.get_books_by_release_year(date(2020, 3, 1))

    # Check that the query returned 3 Books.
    assert len(books) == 3

    # these books are no jokes...
    books = repo.get_books_by_release_year(date(2020, 4, 1))

    # Check that the query returned 5 Books.
    assert len(books) == 5


def test_repository_does_not_retrieve_an_book_when_there_are_no_books_for_a_given_date(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    books = repo.get_books_by_release_year(date(2020, 3, 8))
    assert len(books) == 0


def test_repository_can_retrieve_genres(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genres = repo.get_genres()

    assert len(genres) == 10

    genre_one = [genre for genre in genres if genre.genre_name == 'Horror'][0]
    genre_two = [genre for genre in genres if genre.genre_name == 'Mystery'][0]
    genre_three = [genre for genre in genres if genre.genre_name == 'Thriller'][0]

    assert genre_one.number_of_genre_books == 53
    assert genre_two.number_of_genre_books == 2
    assert genre_three.number_of_genre_books == 64


def test_repository_can_get_first_book(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book = repo.get_first_book()
    assert book.title == 'Coronavirus: First case of virus in New Zealand'


def test_repository_can_get_last_book(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book = repo.get_last_book()
    assert book.title == 'Covid 19 coronavirus: Kiwi mum on the heartbreak of losing her baby in lockdown'


def test_repository_can_get_books_by_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    books = repo.get_books_by_id([2, 5, 6])

    assert len(books) == 3
    assert books[0].title == 'Covid 19 coronavirus: US deaths double in two days, Trump says quarantine not necessary'
    assert books[1].title == "Australia's first coronavirus fatality as man dies in Perth"
    assert books[2].title == 'Coronavirus: Death confirmed as six more test positive in NSW'


def test_repository_does_not_retrieve_book_for_non_existent_id(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    books = repo.get_books_by_id([2, 209])

    assert len(books) == 1
    assert books[0].title == 'Covid 19 coronavirus: US deaths double in two days, Trump says quarantine not necessary'


def test_repository_returns_an_empty_list_for_non_existent_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    books = repo.get_books_by_id([0, 199])

    assert len(books) == 0


def test_repository_returns_book_ids_for_existing_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book_ids = repo.get_book_ids_for_genre('Health')

    assert book_ids == [1, 2]


def test_repository_returns_an_empty_list_for_non_existent_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book_ids = repo.get_book_ids_for_genre('United States')

    assert len(book_ids) == 0


def test_repository_returns_date_of_previous_book(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book = repo.get_book(6)
    previous_date = repo.get_release_year_of_previous_book(book)

    assert previous_date.isoformat() == '2020-03-01'


def test_repository_returns_none_when_there_are_no_previous_books(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book = repo.get_book(1)
    previous_date = repo.get_release_year_of_previous_book(book)

    assert previous_date is None


def test_repository_returns_date_of_next_book(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book = repo.get_book(3)
    next_date = repo.get_release_year_of_next_book(book)

    assert next_date.isoformat() == '2020-03-05'


def test_repository_returns_none_when_there_are_no_subsequent_books(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book = repo.get_book(177)
    next_date = repo.get_release_year_of_next_book(book)

    assert next_date is None


def test_repository_can_add_a_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genre = Genre('Motoring')
    repo.add_genre(genre)

    assert genre in repo.get_genres()


def test_repository_can_add_a_review(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('thorke')
    book = repo.get_book(2)
    review = make_review("Trump's onto it!", user, book)

    repo.add_review(review)

    assert review in repo.get_reviews()


def test_repository_does_not_add_a_review_without_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book = repo.get_book(2)
    user = repo.get_user('thorke')
    review = Review(book, "Absolutely amazing!", user, 5)

    with pytest.raises(RepositoryException):
        repo.add_review(review)


def test_repository_can_retrieve_reviews(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    assert len(repo.get_reviews()) == 3


def make_book(new_book_release_year):
    book = Book(
        new_book_release_year,
        'New Book',
    )
    return book


def test_can_retrieve_an_book_and_add_a_review_to_it(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    # Fetch Book and User.
    book = repo.get_book(5)
    user = repo.get_user('thorke')

    # Create a new Review, connecting it to the Book and User.
    review = make_review('Best book in Australia', user, book)

    book_fetched = repo.get_book(5)
    user_fetched = repo.get_user('thorke')

    assert review in book_fetched.reviews
    assert review in user_fetched.reviews

