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


def get_selected_books(quantity=3):
    books = services.get_random_books(quantity, repo.repo_instance)

    for book in books:
        book['hyperlink'] = url_for('book_bp.books_by_release_year', release_year=book['release_year'])
    return books
