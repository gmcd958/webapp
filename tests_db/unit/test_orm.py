import pytest

import datetime

from sqlalchemy.exc import IntegrityError

from library.domain.model import User, Book, Review, Genre, make_review, make_genre_association

book_release_year = 2013


def insert_user(empty_session, values=None):
    new_name = "Andrew"
    new_password = "1234"

    if values is not None:
        new_name = values[0]
        new_password = values[1]

    empty_session.execute('INSERT INTO users (user_name, password) VALUES (:user_name, :password)',
                          {'user_name': new_name, 'password': new_password})
    row = empty_session.execute('SELECT user_id from users where user_name = :user_name',
                                {'user_name': new_name}).fetchone()
    return row[0]


def insert_users(empty_session, values):
    for value in values:
        empty_session.execute('INSERT INTO users (user_name, password) VALUES (:user_name, :password)',
                              {'user_name': value[0], 'password': value[1]})
    rows = list(empty_session.execute('SELECT user_id from users'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_book(empty_session):
    empty_session.execute(
        'INSERT INTO books (title, release_year, publisher, author) VALUES ("Good Book", :date, 1, 1)',
        {'date': book_release_year}
    )
    row = empty_session.execute('SELECT book_id from books').fetchone()
    return row[0]


def insert_genres(empty_session):
    empty_session.execute(
        'INSERT INTO genres (genre_name) VALUES ("Scary"), ("Super Scary")'
    )
    rows = list(empty_session.execute('SELECT genre_id from genres'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_book_genre_associations(empty_session, book_key, genre_keys):
    stmt = 'INSERT INTO book_genres (book_id, genre_id) VALUES (:book_id, :genre_id)'
    for genre_key in genre_keys:
        empty_session.execute(stmt, {'book_id': book_key, 'genre_id': genre_key})


def insert_reviewed_book(empty_session):
    book_key = insert_book(empty_session)
    user_key = insert_user(empty_session)

    timestamp_1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    timestamp_2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    empty_session.execute(
        'INSERT INTO reviews (user_id, book_id, review_text, rating, timestamp) VALUES '
        '(:user_id, :book_id, "Review 1", 3, :timestamp_1),'
        '(:user_id, :book_id, "Review 2", 4, :timestamp_2)',
        {'user_id': user_key, 'book_id': book_key, 'timestamp_1': timestamp_1, 'timestamp_2': timestamp_2}
    )

    row = empty_session.execute('SELECT book_id from books').fetchone()
    return row[0]


def make_book():
    book = Book(
        book_release_year,
        "Good Book",
        1,
        1,
        1,
    )
    return book


def make_user():
    user = User("Andrew", "1111asdA")
    return user


def make_genre():
    genre = Genre("Crime")
    return genre


def test_loading_of_users(empty_session):
    users = list()
    users.append(("andrew", "1234"))
    users.append(("cindy", "1111"))
    insert_users(empty_session, users)

    expected = [
        User("andrew", "1234"),
        User("cindy", "999")
    ]
    assert empty_session.query(User).all() == expected


def test_saving_of_users(empty_session):
    user = make_user()
    empty_session.add(user)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT user_name, password FROM users'))
    assert rows == [("andrew", "1111asdA")]


def test_saving_of_users_with_common_user_name(empty_session):
    insert_user(empty_session, ("Andrew", "1234"))
    empty_session.commit()

    with pytest.raises(IntegrityError):
        user = User("Andrew", "111")
        empty_session.add(user)
        empty_session.commit()


def test_loading_of_book(empty_session):
    book_key = insert_book(empty_session)
    expected_book = make_book()
    fetched_book = empty_session.query(Book).one()

    assert expected_book == fetched_book
    assert book_key == fetched_book.book_id


def test_loading_of_genred_book(empty_session):
    book_key = insert_book(empty_session)
    genre_keys = insert_genres(empty_session)
    insert_book_genre_associations(empty_session, book_key, genre_keys)

    book = empty_session.query(Book).get(book_key)
    genres = [empty_session.query(Genre).get(key) for key in genre_keys]

    for genre in genres:
        assert book.is_genred_by(genre)
        assert genre.is_applied_to(book)


def test_loading_of_reviewed_book(empty_session):
    insert_reviewed_book(empty_session)

    rows = empty_session.query(Book).all()
    book = rows[0]

    for review in book.reviews:
        assert review.book is book


def test_saving_of_review(empty_session):
    book_key = insert_book(empty_session)
    user_key = insert_user(empty_session, ("Andrew", "1234"))

    rows = empty_session.query(Book).all()
    book = rows[0]
    user = empty_session.query(User).filter(User._User__user_name == "Andrew").one()

    # Create a new Review that is bidirectionally linked with the User and Book.
    review_text = "Some review text."
    review = make_review(review_text, user, book, 5)

    # Note: if the bidirectional links between the new Review and the User and
    # Book objects hadn't been established in memory, they would exist following
    # committing the addition of the Review to the database.
    empty_session.add(review)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT user_id, book_id, review_text FROM reviews'))

    assert rows == [(user_key, book_key, review_text)]


def test_saving_of_book(empty_session):
    book = make_book()
    empty_session.add(book)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT release_year, title, author, publisher FROM books'))
    release_year = book_release_year
    assert rows == [(release_year, "Good Book", 1, 1)]


def test_saving_genred_book(empty_session):
    book = make_book()
    genre = make_genre()

    # Establish the bidirectional relationship between the Book and the Genre.
    make_genre_association(book, genre)

    # Persist the Book (and Genre).
    # Note: it doesn't matter whether we add the Genre or the Book. They are connected
    # bidirectionally, so persisting either one will persist the other.
    empty_session.add(book)
    empty_session.commit()

    # Test test_saving_of_book() checks for insertion into the books table.
    rows = list(empty_session.execute('SELECT book_id FROM books'))
    book_key = rows[0][0]

    # Check that the genres table has a new record.
    rows = list(empty_session.execute('SELECT genre_id, genre_name FROM genres'))
    genre_key = rows[0][0]
    assert rows[0][1] == "Crime"

    # Check that the book_genres table has a new record.
    rows = list(empty_session.execute('SELECT book_id, genre_id from book_genres'))
    book_foreign_key = rows[0][0]
    genre_foreign_key = rows[0][1]

    assert book_key == book_foreign_key
    assert genre_key == genre_foreign_key


def test_save_reviewed_book(empty_session):
    # Create Book User objects.
    book = make_book()
    user = make_user()

    # Create a new Review that is bidirectionally linked with the User and Book.
    review_text = "Some review text."
    review = make_review(review_text, user, book, 4)

    # Save the new Book.
    empty_session.add(book)
    empty_session.commit()

    # Test test_saving_of_book() checks for insertion into the books table.
    rows = list(empty_session.execute('SELECT book_id FROM books'))
    book_key = rows[0][0]

    # Test test_saving_of_users() checks for insertion into the users table.
    rows = list(empty_session.execute('SELECT user_id FROM users'))
    user_key = rows[0][0]

    # Check that the reviews table has a new record that links to the books and users
    # tables.
    rows = list(empty_session.execute('SELECT user_id, book_id, review_text FROM reviews'))
    assert rows == [(user_key, book_key, review_text)]