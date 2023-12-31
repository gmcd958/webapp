from datetime import date

from flask import Blueprint
from flask import request, render_template, redirect, url_for, session

from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

import library.adapters.repository as repo
import library.utilities.utilities as utilities
import library.book.services as services

from library.authentication.authentication import login_required


# Configure Blueprint.
book_blueprint = Blueprint(
    'book_bp', __name__)


@book_blueprint.route('/books_by_release_year', methods=['GET'])
def books_by_release_year():
    # Read query parameters.
    target_year = request.args.get('release_year')
    book_to_show_reviews = request.args.get('view_reviews_for')

    # Fetch the first and last articles in the series.
    first_book = services.get_first_book(repo.repo_instance)
    last_book = services.get_last_book(repo.repo_instance)

    if target_year is None:
        # No date query parameter, so return articles from day 1 of the series.
        target_year = first_book['release_year']
    else:
        # Convert target_date from string to int.
        target_year = int(target_year)

    if book_to_show_reviews is None:
        # No view-comments query parameter, so set to a non-existent article id.
        book_to_show_reviews = -1
    else:
        # Convert article_to_show_comments from string to int.
        book_to_show_reviews = int(book_to_show_reviews)

    # Fetch article(s) for the target date. This call also returns the previous and next dates for articles immediately
    # before and after the target date.
    books, previous_year, next_year = services.get_books_by_release_year(target_year, repo.repo_instance)

    first_book_url = None
    last_book_url = None
    next_book_url = None
    prev_book_url = None

    if len(books) > 0:
        # There's at least one article for the target date.
        if previous_year is not None:
            # There are articles on a previous date, so generate URLs for the 'previous' and 'first' navigation buttons.
            prev_book_url = url_for('book_bp.books_by_release_year', release_year=previous_year)
            first_book_url = url_for('book_bp.books_by_release_year', release_year=first_book['release_year'])

        # There are articles on a subsequent date, so generate URLs for the 'next' and 'last' navigation buttons.
        if next_year is not None:
            next_book_url = url_for('book_bp.books_by_release_year', release_year=next_year)
            last_book_url = url_for('book_bp.books_by_release_year', release_year=last_book['release_year'])

        # Construct urls for viewing article comments and adding comments.
        for book in books:
            book['view_review_url'] = url_for('book_bp.books_by_release_year', release_year=target_year, view_reviews_for=book['book_id'])
            book['add_review_url'] = url_for('book_bp.review_on_book', book=book['book_id'])

        # Generate the webpage to display the articles.
        return render_template(
            'book/books.html',
            title=target_year,
            book_year=target_year,
            books=books,
            selected_books=utilities.get_selected_books(3),
            genre_urls=utilities.get_genres_and_urls(),
            author_urls=utilities.get_authors_and_urls(),
            publisher_urls=utilities.get_publishers_and_urls(),
            first_book_url=first_book_url,
            last_book_url=last_book_url,
            prev_book_url=prev_book_url,
            next_book_url=next_book_url,
            show_reviews_for_book=book_to_show_reviews
        )

    # No articles to show, so return the homepage.
    return redirect(url_for('home_bp.home'))


@book_blueprint.route('/list_of_authors', methods=['GET'])
def list_of_authors():
    authors = utilities.get_genres_and_urls()
    if len(authors) > 0:
        return render_template(
            'book/authors.html',
            title='Authors',
            selected_books=utilities.get_selected_books(3),
            author_urls=utilities.get_authors_and_urls()
        )
    # No articles to show, so return the homepage.
    return redirect(url_for('home_bp.home'))


@book_blueprint.route('/books_by_author', methods=['GET'])
def books_by_author():
    books_per_page = 3

    # Read query parameters.
    author_name = request.args.get('author')
    cursor = request.args.get('cursor')
    book_to_show_reviews = request.args.get('view_reviews_for')

    if book_to_show_reviews is None:
        # No view-comments query parameter, so set to a non-existent article id.
        book_to_show_reviews = -1
    else:
        # Convert article_to_show_comments from string to int.
        book_to_show_reviews = int(book_to_show_reviews)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve article ids for articles that are tagged with tag_name.
    book_ids = services.get_book_ids_for_author(author_name, repo.repo_instance)

    # Retrieve the batch of articles to display on the Web page.
    books = services.get_books_by_id(book_ids[cursor:cursor + books_per_page], repo.repo_instance)

    first_book_url = None
    last_book_url = None
    next_book_url = None
    prev_book_url = None

    if cursor > 0:
        # There are preceding articles, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_book_url = url_for('book_bp.books_by_author', author=author_name, cursor=cursor - books_per_page)
        first_book_url = url_for('book_bp.books_by_author', author=author_name)

    if cursor + books_per_page < len(book_ids):
        # There are further articles, so generate URLs for the 'next' and 'last' navigation buttons.
        next_book_url = url_for('book_bp.books_by_author', author=author_name, cursor=cursor + books_per_page)

        last_cursor = books_per_page * int(len(book_ids) / books_per_page)
        if len(book_ids) % books_per_page == 0:
            last_cursor -= books_per_page
        last_book_url = url_for('book_bp.books_by_author', author=author_name, cursor=last_cursor)

    # Construct urls for viewing article comments and adding comments.
    for book in books:
        book['view_review_url'] = url_for('book_bp.books_by_author', author=author_name, cursor=cursor, view_reviews_for=book['book_id'])
        book['add_review_url'] = url_for('book_bp.review_on_book', book=book['book_id'])

    # Generate the webpage to display the articles.
    return render_template(
        'book/books.html',
        title=author_name,
        books_authors='Books categorised by ' + author_name,
        books=books,
        selected_books=utilities.get_selected_books(3),
        genre_urls=utilities.get_genres_and_urls(),
        author_urls=utilities.get_authors_and_urls(),
        publisher_urls=utilities.get_publishers_and_urls(),
        first_book_url=first_book_url,
        last_book_url=last_book_url,
        prev_book_url=prev_book_url,
        next_book_url=next_book_url,
        show_reviews_for_book=book_to_show_reviews
    )


@book_blueprint.route('/list_of_publishers', methods=['GET'])
def list_of_publishers():
    publishers = utilities.get_publishers_and_urls()
    if len(publishers) > 0:
        return render_template(
            'book/publishers.html',
            title='Publishers',
            selected_books=utilities.get_selected_books(3),
            publisher_urls=utilities.get_publishers_and_urls(),
        )
    # No articles to show, so return the homepage.
    return redirect(url_for('home_bp.home'))


@book_blueprint.route('/books_by_publisher', methods=['GET'])
def books_by_publisher():
    books_per_page = 3

    # Read query parameters.
    publisher_name = request.args.get('publisher')
    cursor = request.args.get('cursor')
    book_to_show_reviews = request.args.get('view_reviews_for')

    if book_to_show_reviews is None:
        # No view-comments query parameter, so set to a non-existent article id.
        book_to_show_reviews = -1
    else:
        # Convert article_to_show_comments from string to int.
        book_to_show_reviews = int(book_to_show_reviews)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve article ids for articles that are tagged with tag_name.
    book_ids = services.get_book_ids_for_publisher(publisher_name, repo.repo_instance)

    # Retrieve the batch of articles to display on the Web page.
    books = services.get_books_by_id(book_ids[cursor:cursor + books_per_page], repo.repo_instance)

    first_book_url = None
    last_book_url = None
    next_book_url = None
    prev_book_url = None

    if cursor > 0:
        # There are preceding articles, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_book_url = url_for('book_bp.books_by_publisher', publisher=publisher_name, cursor=cursor - books_per_page)
        first_book_url = url_for('book_bp.books_by_publisher', publisher=publisher_name)

    if cursor + books_per_page < len(book_ids):
        # There are further articles, so generate URLs for the 'next' and 'last' navigation buttons.
        next_book_url = url_for('book_bp.books_by_publisher', publisher=publisher_name, cursor=cursor + books_per_page)

        last_cursor = books_per_page * int(len(book_ids) / books_per_page)
        if len(book_ids) % books_per_page == 0:
            last_cursor -= books_per_page
        last_book_url = url_for('book_bp.books_by_publisher', publisher=publisher_name, cursor=last_cursor)

    # Construct urls for viewing article comments and adding comments.
    for book in books:
        book['view_review_url'] = url_for('book_bp.books_by_publisher', publisher=publisher_name, cursor=cursor, view_reviews_for=book['book_id'])
        book['add_review_url'] = url_for('book_bp.review_on_book', book=book['book_id'])

    # Generate the webpage to display the articles.
    return render_template(
        'book/books.html',
        title=publisher_name,
        books_publisher='Books published by ' + publisher_name,
        books=books,
        selected_books=utilities.get_selected_books(3),
        genre_urls=utilities.get_genres_and_urls(),
        author_urls=utilities.get_authors_and_urls(),
        publisher_urls=utilities.get_publishers_and_urls(),
        first_book_url=first_book_url,
        last_book_url=last_book_url,
        prev_book_url=prev_book_url,
        next_book_url=next_book_url,
        show_reviews_for_book=book_to_show_reviews
    )


@book_blueprint.route('/list_of_genres', methods=['GET'])
def list_of_genres():
    genres = utilities.get_genres_and_urls()
    if len(genres) > 0:
        return render_template(
            'book/genres.html',
            title='Genres',
            selected_books=utilities.get_selected_books(3),
            genre_urls=utilities.get_genres_and_urls(),
        )
    # No articles to show, so return the homepage.
    return redirect(url_for('home_bp.home'))


@book_blueprint.route('/books_by_genre', methods=['GET'])
def books_by_genre():
    books_per_page = 3

    # Read query parameters.
    genre_name = request.args.get('genre')
    cursor = request.args.get('cursor')
    book_to_show_reviews = request.args.get('view_reviews_for')

    if book_to_show_reviews is None:
        # No view-comments query parameter, so set to a non-existent article id.
        book_to_show_reviews = -1
    else:
        # Convert article_to_show_comments from string to int.
        book_to_show_reviews = int(book_to_show_reviews)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve article ids for articles that are tagged with tag_name.
    book_ids = services.get_book_ids_for_genre(genre_name, repo.repo_instance)

    # Retrieve the batch of articles to display on the Web page.
    books = services.get_books_by_id(book_ids[cursor:cursor + books_per_page], repo.repo_instance)

    first_book_url = None
    last_book_url = None
    next_book_url = None
    prev_book_url = None

    if cursor > 0:
        # There are preceding articles, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_book_url = url_for('book_bp.books_by_genre', genre=genre_name, cursor=cursor - books_per_page)
        first_book_url = url_for('book_bp.books_by_genre', genre=genre_name)

    if cursor + books_per_page < len(book_ids):
        # There are further articles, so generate URLs for the 'next' and 'last' navigation buttons.
        next_book_url = url_for('book_bp.books_by_genre', genre=genre_name, cursor=cursor + books_per_page)

        last_cursor = books_per_page * int(len(book_ids) / books_per_page)
        if len(book_ids) % books_per_page == 0:
            last_cursor -= books_per_page
        last_book_url = url_for('book_bp.books_by_genre', genre=genre_name, cursor=last_cursor)

    # Construct urls for viewing article comments and adding comments.
    for book in books:
        book['view_review_url'] = url_for('book_bp.books_by_genre', genre=genre_name, cursor=cursor, view_reviews_for=book['book_id'])
        book['add_review_url'] = url_for('book_bp.review_on_book', book=book['book_id'])

    # Generate the webpage to display the articles.
    return render_template(
        'book/books.html',
        title=genre_name,
        books_genres='Books categorised by ' + genre_name,
        books=books,
        selected_books=utilities.get_selected_books(3),
        genre_urls=utilities.get_genres_and_urls(),
        author_urls=utilities.get_authors_and_urls(),
        publisher_urls=utilities.get_publishers_and_urls(),
        first_book_url=first_book_url,
        last_book_url=last_book_url,
        prev_book_url=prev_book_url,
        next_book_url=next_book_url,
        show_reviews_for_book=book_to_show_reviews
    )


@book_blueprint.route('/review', methods=['GET', 'POST'])
@login_required
def review_on_book():
    # Obtain the user name of the currently logged in user.
    user_name = session['user_name']

    # Create form. The form maintains state, e.g. when this method is called with a HTTP GET request and populates
    # the form with an article id, when subsequently called with a HTTP POST request, the article id remains in the
    # form.
    form = CommentForm()

    if form.validate_on_submit():
        # Successful POST, i.e. the comment text has passed data validation.
        # Extract the article id, representing the commented article, from the form.
        book_id = int(form.book_id.data)

        # Use the service layer to store the new comment.
        services.add_review(book_id, form.review.data, user_name, int(form.review_rating.data), repo.repo_instance)

        # Retrieve the article in dict form.
        book = services.get_book(book_id, repo.repo_instance)

        # Cause the web browser to display the page of all articles that have the same date as the commented article,
        # and display all comments, including the new comment.
        return redirect(url_for('book_bp.books_by_release_year', release_year=book['release_year'], view_reviews_for=book_id))

    if request.method == 'GET':
        # Request is a HTTP GET to display the form.
        # Extract the article id, representing the article to comment, from a query parameter of the GET request.
        book_id = int(request.args.get('book'))

        # Store the article id in the form.
        form.book_id.data = book_id
    else:
        # Request is a HTTP POST where form validation has failed.
        # Extract the article id of the article being commented from the form.
        book_id = int(form.book_id.data)

    # For a GET or an unsuccessful POST, retrieve the article to comment in dict form, and return a Web page that allows
    # the user to enter a comment. The generated Web page includes a form object.
    book = services.get_book(book_id, repo.repo_instance)
    return render_template(
        'book/review_on_book.html',
        title='Edit book review',
        book=book,
        form=form,
        handler_url=url_for('book_bp.review_on_book'),
        selected_books=utilities.get_selected_books(3),
        genre_urls=utilities.get_genres_and_urls(),
        author_urls=utilities.get_authors_and_urls(),
        publisher_urls=utilities.get_publishers_and_urls()
    )


class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)


class CommentForm(FlaskForm):
    review = TextAreaField('Review', [
        DataRequired(),
        Length(min=4, message='Your review is too short'),
        ProfanityFree(message='Your review must not contain profanity')])
    review_rating = TextAreaField('Review_rating', [
        DataRequired(),
        Length(min=1, max=1, message='Your review rating has to be from 1 to 5')])
    book_id = HiddenField("Book id")
    submit = SubmitField('Submit')
