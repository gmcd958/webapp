import pytest
from datetime import date

from library.domain.model import User, Book, Genre, make_review, make_genre_association, ModelException, Author, \
    Publisher


@pytest.fixture()
def book():
    return Book(
        1997,
        'Harry Potter',
        1,
        1,
        1,
    )


@pytest.fixture()
def user():
    return User('dbowie', '1234567890')


@pytest.fixture()
def genre():
    return Genre('Horror')


@pytest.fixture()
def author():
    return Author(1, 'James Reiner')


@pytest.fixture()
def publisher():
    return Publisher(1, 'Penguin')


def test_user_construction(user):
    assert user.user_name == 'dbowie'
    assert user.password == '1234567890'
    assert repr(user) == 'dbowie'

    for review in user.reviews:
        # User should have an empty list of Comments after construction.
        assert False


def test_book_construction(book):
    assert book.book_id is 1
    assert book.release_year == 1997
    assert book.title == 'Harry Potter'

    assert book.number_of_reviews == 0
    assert book.number_of_genres == 0

    assert repr(
        book) == '<Book Harry Potter, book id = 1>'


def test_book_less_than_operator():
    book_1 = Book(1999, None, None, None, 1)

    book_2 = Book(2000, None, None, None, 2)

    assert book_1 < book_2


def test_genre_construction(genre):
    assert genre.genre_name == 'Horror'

    for book in genre.genre_books:
        assert False

    assert not genre.is_applied_to(Book(0, None, None))


def test_author_construction(author):
    assert author.full_name == 'James Reiner'

    for book in author.books:
        assert False


def test_publisher_construction(publisher):
    assert publisher.name == 'Penguin'

    for book in publisher.books:
        assert False


def test_make_review_establishes_relationships(book, user):
    review_text = 'Very good'
    review = make_review(review_text, user, book, 5)

    # Check that the User object knows about the Comment.
    assert review in user.reviews

    # Check that the Comment knows about the User.
    assert review.user is user

    # Check that Article knows about the Comment.
    assert review in book.reviews

    # Check that the Comment knows about the Article.
    assert review.book is book


def test_make_genre_associations(book, genre):
    make_genre_association(book, genre)

    # Check that the Article knows about the Tag.
    assert book.is_genred()
    assert book.is_genred_by(genre)

    # check that the Tag knows about the Article.
    assert genre.is_applied_to(book)
    assert book in genre.genre_books


def test_make_genre_associations_with_book_already_genred(book, genre):
    make_genre_association(book, genre)

    with pytest.raises(ModelException):
        make_genre_association(book, genre)
