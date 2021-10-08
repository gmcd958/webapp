from pathlib import Path


from library.adapters.csv_data_importer import load_authors, load_books_and_genres, load_users, load_reviews
from library.adapters.repository import AbstractRepository


def populate(data_path: Path, repo: AbstractRepository, database_mode: bool):
    # Load authors into the repository.
    authors = load_authors(data_path, repo)

    # Load books and genres into the repository.
    load_books_and_genres(data_path, repo, authors, database_mode)

    # Load users into the repository.
    users = load_users(data_path, repo)

    # Load comments into the repository.
    load_reviews(data_path, repo, users)
