import pytest

from flask import session


def test_register(client):
    # Check that we retrieve the register page.
    response_code = client.get('/authentication/register').status_code
    assert response_code == 200

    # Check that we can register a user successfully, supplying a valid user name and password.
    response = client.post(
        '/authentication/register',
        data={'user_name': 'gmichael', 'password': 'CarelessWhisper1984'}
    )
    assert response.headers['Location'] == 'http://localhost/authentication/login'


@pytest.mark.parametrize(('user_name', 'password', 'message'), (
        ('', '', b'Your user name is required'),
        ('cj', '', b'Your user name is too short'),
        ('test', '', b'Your password is required'),
        ('test', 'test', b'Your password must be at least 8 characters, and contain an upper case letter,\
            a lower case letter and a digit'),
        ('fmercury', 'Test#6^0', b'Your user name is already taken - please supply another'),
))
def test_register_with_invalid_input(client, user_name, password, message):
    # Check that attempting to register with invalid combinations of user name and password generate appropriate error
    # messages.
    response = client.post(
        '/authentication/register',
        data={'user_name': user_name, 'password': password}
    )
    assert message in response.data


def test_login(client, auth):
    # Check that we can retrieve the login page.
    status_code = client.get('/authentication/login').status_code
    assert status_code == 200

    # Check that a successful login generates a redirect to the homepage.
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    # Check that a session has been created for the logged-in user.
    with client:
        client.get('/')
        assert session['user_name'] == 'thorke'


def test_logout(client, auth):
    # Login a user.
    auth.login()

    with client:
        # Check that logging out clears the user's session.
        auth.logout()
        assert 'user_id' not in session


def test_index(client):
    # Check that we can retrieve the home page.
    response = client.get('/')
    assert response.status_code == 200


def test_login_required_to_review(client):
    response = client.post('/review')
    assert response.headers['Location'] == 'http://localhost/authentication/login'


def test_review(client, auth):
    # Login a user.
    auth.login()

    # Check that we can retrieve the review page.
    response = client.get('/review?book=1')

    response = client.post(
        '/review',
        data={'review': "Wowowowowow", 'review_rating': 4, 'book_id': 1}
    )
    assert response.headers['Location'] == 'http://localhost/books_by_release_year?release_year=1987&view_reviews_for=1'


@pytest.mark.parametrize(('review_text', 'messages'), (
        ('Who thinks Trump is a f***wit?', (b'Your review must not contain profanity')),
        ('Hey', (b'Your review is too short')),
))
def test_review_with_invalid_input(client, auth, review_text, messages):
    # Login a user.
    auth.login()

    response = client.get('/review?book=1')

    # Attempt to review on an book.
    response = client.post(
        '/review',
        data={'review': review_text, 'review_rating': 4, 'book_id': 1}
    )
    # Check that supplying invalid review text generates appropriate error messages.
    for message in messages:
        assert message in response.data


def test_book_without_release_year(client):
    # Check that we can retrieve the books page.
    response = client.get('/books_by_release_year')
    assert response.status_code == 200

    # Check that without providing a date query parameter the page includes the first book.
    assert b'1987' in response.data
    assert b'The House of Memory' in response.data


def test_book_with_release_year(client):
    # Check that we can retrieve the books page.
    response = client.get('/books_by_release_year?release_year=2016')
    assert response.status_code == 302

    # Check that all books on the requested date are included on the page.
    assert b'Redirecting' in response.data


def test_books_with_review(client):
    # Check that we can retrieve the books page.
    response = client.get('/books_by_release_year?release_year=1987&view_reviews_for=1')
    assert response.status_code == 200

    # Check that all reviews for specified book are included on the page.
    assert b"I haven&#39;t read a fun mystery book in a while" in response.data


def test_books_with_genre(client):
    # Check that we can retrieve the books page.
    response = client.get('/books_by_genre?genre=Crime')
    assert response.status_code == 200

    # Check that all books tagged with 'Health' are included on the page.
    assert b'Crime' in response.data
    assert b'Bad book no publisher' in response.data
    assert b'The House of Memory' in response.data


def test_books_with_author(client):
    # Check that we can retrieve the books page.
    response = client.get('/books_by_author?author=James+Reiner')
    assert response.status_code == 200

    # Check that all books tagged with 'Health' are included on the page.
    assert b'James Reiner' in response.data
    assert b'Bad book no publisher' in response.data
    assert b'The House of Memory' in response.data


def test_books_with_publisher(client):
    # Check that we can retrieve the books page.
    response = client.get('/books_by_publisher?publisher=None')
    assert response.status_code == 200

    # Check that all books tagged with 'Health' are included on the page.
    assert b'None' in response.data
    assert b'Bad book no publisher' in response.data
    assert b'The House of Memory' in response.data
