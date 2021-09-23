from flask import Blueprint, request, render_template, redirect, url_for, session

import library.adapters.repository as repo
import library.utilities.services as services


# Configure Blueprint.
utilities_blueprint = Blueprint(
    'utilities_bp', __name__)


def get_genres_and_urls():
    genre_names = services.get_genre_names(repo.repo_instance)
    genre_urls = dict()
    for genre_name in genre_names:
        genre_urls[genre_name] = url_for('book_bp.books_by_genre', genre=genre_name)

    return genre_urls


def get_authors_and_urls():
    author_names = services.get_author_names(repo.repo_instance)
    author_urls = dict()
    for author_name in author_names:
        author_urls[author_name] = url_for('book_bp.books_by_author', author=author_name)

    return author_urls


def get_publishers_and_urls():
    publisher_names = services.get_publisher_names(repo.repo_instance)
    publisher_urls = dict()
    for publisher_name in publisher_names:
        publisher_urls[publisher_name] = url_for('book_bp.books_by_publisher', publisher=publisher_name)

    return publisher_urls


def get_selected_books(quantity=3):
    books = services.get_random_books(quantity, repo.repo_instance)

    for book in books:
        book['hyperlink'] = url_for('book_bp.books_by_release_year', release_year=book['release_year'])
    return books
