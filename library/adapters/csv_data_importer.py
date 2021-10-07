import csv
from pathlib import Path

from werkzeug.security import generate_password_hash

from library.adapters.repository import AbstractRepository
from library.domain.model import Publisher, Author, Book, User, Genre, make_genre_association, make_review


def read_csv_file(filename: str):
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        # Read first line of the the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row


def load_authors(data_path: Path, repo: AbstractRepository):
    authors = dict()

    authors_filename = str(Path(data_path) / "authors.csv")
    for data_row in read_csv_file(authors_filename):
        author = Author(
            author_id=int(data_row[0]),
            author_full_name=data_row[1]
        )
        repo.add_author(author)
        authors[data_row[0]] = author
    return authors


def load_books_and_genres(data_path: Path, repo: AbstractRepository, authors, database_mode: bool):
    genres = dict()
    publishers = dict()

    books_filename = str(data_path / "books.csv")

    for data_row in read_csv_file(books_filename):

        book_id = int(data_row[0])
        number_of_genres = len(data_row) - 7
        book_genres = data_row[-number_of_genres:]

        # Add any new genres; associate the current book with genres.
        for genre in book_genres:
            if genre.strip() != "":
                if genre not in genres.keys():
                    genres[genre] = list()
                genres[genre].append(book_id)
        del data_row[-number_of_genres:]

        # Create Book object.
        book = Book(
            book_id=book_id,
            release_year=int(data_row[1]),
            book_title=data_row[2],
        )

        publisher = Publisher(data_row[3])
        repo.add_publisher(publisher)
        publishers[publisher.name] = publisher
        publishers[publisher.name].add_book(book)

        book.author = authors[data_row[4]]
        authors[data_row[4]].add_book(book)

        book.description = data_row[5]
        book.imgurl = data_row[6]

        repo.add_book(book)

    # Create Genre objects, associate them with Books and add them to the repository.
    for genre_name in genres.keys():
        genre = Genre(genre_name)
        for book_id in genres[genre_name]:
            book = repo.get_book(book_id)
            if database_mode is True:
                book.add_genre(genre)
            else:
                make_genre_association(book, genre)
        repo.add_genre(genre)


def load_users(data_path: Path, repo: AbstractRepository):
    users = dict()

    users_filename = str(Path(data_path) / "users.csv")
    for data_row in read_csv_file(users_filename):
        user = User(
            user_name=data_row[1],
            password=generate_password_hash(data_row[2])
        )
        repo.add_user(user)
        users[data_row[0]] = user
    return users


def load_reviews(data_path: Path, repo: AbstractRepository, users):
    reviews_filename = str(Path(data_path) / "reviews.csv")
    for data_row in read_csv_file(reviews_filename):
        review = make_review(
            review_text=data_row[2],
            user=users[data_row[0]],
            book=repo.get_book(int(data_row[1])),
            rating=int(data_row[3])
        )
        repo.add_review(review)