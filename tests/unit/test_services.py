from datetime import date

import pytest

from library.authentication.services import AuthenticationException
from library.book import services as book_services
from library.authentication import services as auth_services
from library.book.services import NonExistentBookException
from library.domain.model import Author


def test_can_add_user(in_memory_repo):
    new_user_name = 'jz'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)

    user_as_dict = auth_services.get_user(new_user_name, in_memory_repo)
    assert user_as_dict['user_name'] == new_user_name

    # Check that password has been encrypted.
    assert user_as_dict['password'].startswith('pbkdf2:sha256:')


def test_cannot_add_user_with_existing_name(in_memory_repo):
    user_name = 'thorke'
    password = 'abcd1A23'

    with pytest.raises(auth_services.NameNotUniqueException):
        auth_services.add_user(user_name, password, in_memory_repo)


def test_authentication_with_valid_credentials(in_memory_repo):
    new_user_name = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)

    try:
        auth_services.authenticate_user(new_user_name, new_password, in_memory_repo)
    except AuthenticationException:
        assert False


def test_authentication_with_invalid_credentials(in_memory_repo):
    new_user_name = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)

    with pytest.raises(auth_services.AuthenticationException):
        auth_services.authenticate_user(new_user_name, '0987654321', in_memory_repo)


def test_can_add_review(in_memory_repo):
    book_id = 1
    review_text = 'Not bad, good size'
    user_name = 'thorke'

    # Call the service layer to add the review.
    book_services.add_review(book_id, review_text, user_name, 5, in_memory_repo)

    # Retrieve the reviews for the book from the repository.
    reviews_as_dict = book_services.get_reviews_for_book(book_id, in_memory_repo)

    # Check that the reviews include a review with the new review text.
    assert next(
        (dictionary['review_text'] for dictionary in reviews_as_dict if dictionary['review_text'] == review_text),
        None) is not None


def test_cannot_add_review_for_non_existent_book(in_memory_repo):
    book_id = 100
    review_text = "Absolutely horrible"
    user_name = 'fmercury'

    # Call the service layer to attempt to add the review.
    with pytest.raises(book_services.NonExistentBookException):
        book_services.add_review(book_id, review_text, user_name, 1, in_memory_repo)


def test_cannot_add_review_by_unknown_user(in_memory_repo):
    book_id = 3
    review_text = 'I am anon'
    user_name = 'gmichael'

    # Call the service layer to attempt to add the review.
    with pytest.raises(book_services.UnknownUserException):
        book_services.add_review(book_id, review_text, user_name, 3, in_memory_repo)


def test_can_get_book(in_memory_repo):
    book_id = 1

    book_as_dict = book_services.get_book(book_id, in_memory_repo)

    assert book_as_dict['book_id'] == book_id
    assert book_as_dict['release_year'] == 1987
    assert book_as_dict['title'] == 'The House of Memory'
    assert book_as_dict['imgurl'] == 'https://images.gr-assets.com/books/1493114742m/33394837.jpg'
    assert book_as_dict['author_id'] == 1
    assert book_as_dict['description'] == 'Bad book no publisher'
    assert len(book_as_dict['reviews']) == 1

    genre_names = [dictionary['genre_name'] for dictionary in book_as_dict['genres']]
    assert 'Crime' in genre_names


def test_cannot_get_book_with_non_existent_id(in_memory_repo):
    book_id = 100

    # Call the service layer to attempt to retrieve the Article.
    with pytest.raises(book_services.NonExistentBookException):
        book_services.get_book(book_id, in_memory_repo)


def test_get_first_book(in_memory_repo):
    book_as_dict = book_services.get_first_book(in_memory_repo)

    assert book_as_dict['release_year'] == 1987


def test_get_last_book(in_memory_repo):
    book_as_dict = book_services.get_last_book(in_memory_repo)

    assert book_as_dict['release_year'] == 2016


def test_get_books_by_date_with_one_date(in_memory_repo):
    target_year = 1987

    books_as_dict, prev_year, next_year = book_services.get_books_by_release_year(target_year, in_memory_repo)

    assert len(books_as_dict) == 2
    assert books_as_dict[0]['book_id'] == 1

    assert prev_year is None
    assert next_year == 1988


def test_get_books_by_release_year_with_multiple_dates(in_memory_repo):
    target_year = 2003

    books_as_dict, prev_year, next_year = book_services.get_books_by_release_year(target_year, in_memory_repo)

    assert len(books_as_dict) == 2

    # Check that the book ids for the the books returned are 3, 4 and 5.
    book_ids = [book['book_id'] for book in books_as_dict]
    assert {7, 8}.issubset(book_ids)

    # Check that the dates of books surrounding the target_date are 2020-02-29 and 2020-03-05.
    assert prev_year == 1996
    assert next_year == 2008


def test_get_books_by_release_year_with_non_existent_year(in_memory_repo):
    target_year = 1234

    books_as_dict, prev_year, next_year = book_services.get_books_by_release_year(target_year, in_memory_repo)

    # Check that there are no books dated 2020-03-06.
    assert len(books_as_dict) == 0


def test_get_books_by_id(in_memory_repo):
    target_book_ids = [1, 2, 99, 100]
    books_as_dict = book_services.get_books_by_id(target_book_ids, in_memory_repo)

    # Check that 2 books were returned from the query.
    assert len(books_as_dict) == 2

    # Check that the book ids returned were 5 and 6.
    book_ids = [book['book_id'] for book in books_as_dict]
    assert {1, 2}.issubset(book_ids)


def test_get_reviews_for_book(in_memory_repo):
    reviews_as_dict = book_services.get_reviews_for_book(1, in_memory_repo)

    # Check that 2 reviews were returned for book with id 1.
    assert len(reviews_as_dict) == 1

    # Check that the reviews relate to the book whose id is 1.
    book_ids = [review['book_id'] for review in reviews_as_dict]
    book_ids = set(book_ids)
    assert 1 in book_ids and len(book_ids) == 1


def test_get_reviews_for_non_existent_book(in_memory_repo):
    with pytest.raises(NonExistentBookException):
        reviews_as_dict = book_services.get_reviews_for_book(99, in_memory_repo)


def test_get_reviews_for_book_without_reviews(in_memory_repo):
    reviews_as_dict = book_services.get_reviews_for_book(20, in_memory_repo)
    assert len(reviews_as_dict) == 0

