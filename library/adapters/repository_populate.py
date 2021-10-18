from pathlib import Path


from library.adapters.csv_data_importer import load_authors, load_publishers, load_books_and_genres, load_users, load_reviews
from library.adapters.repository import AbstractRepository


def populate(data_path: Path, repo: AbstractRepository, database_mode: bool):
    # Load authors into the repository.
    authors = load_authors(data_path, repo)

    #print('loaded authors')

    # Load publishers into the repository.
    publishers = load_publishers(data_path, repo)

    #print('loaded publishers')

    # Load books and genres into the repository.
    load_books_and_genres(data_path, repo, authors, publishers, database_mode)

    #print('loaded books and genres')

    # Load users into the repository.
    users = load_users(data_path, repo)

    #print('loaded users')

    # Load comments into the repository.
    load_reviews(data_path, repo, users)

    #print('loaded reviews')
