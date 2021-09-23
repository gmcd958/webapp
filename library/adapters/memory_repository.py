import csv
from pathlib import Path
from datetime import date, datetime
from typing import List

from bisect import bisect, bisect_left, insort_left

from werkzeug.security import generate_password_hash

from library.adapters.repository import AbstractRepository, RepositoryException
from library.domain.model import Publisher, Author, Book, Review, User, BooksInventory, Genre, make_genre_association, \
    make_review


class MemoryRepository(AbstractRepository):
    # Articles ordered by date, not id. id is assumed unique.

    def __init__(self):
        self.__books = list()
        self.__books_index = dict()
        self.__authors = list()
        self.__publishers = list()
        self.__genres = list()
        self.__users = list()
        self.__reviews = list()

    def add_user(self, user: User):
        self.__users.append(user)

    def get_user(self, user_name) -> User:
        return next((user for user in self.__users if user.user_name == user_name), None)

    def add_book(self, book: Book):
        insort_left(self.__books, book)
        self.__books_index[book.book_id] = book

    def get_book(self, book_id: int) -> Book:
        book = None

        try:
            book = self.__books_index[book_id]
        except KeyError:
            pass  # Ignore exception and return None.

        return book

    def get_all_books(self) -> List[Book]:
        return self.__books

    def get_books_by_release_year(self, target_year) -> List[Book]:
        matching_books = list()
        try:
            for book in self.__books:
                if book.release_year == target_year:
                    matching_books.append(book)
        except ValueError:
            # No articles for specified date. Simply return an empty list.
            pass

        return matching_books

    def get_number_of_books(self):
        return len(self.__books)

    def get_first_book(self):
        book = None

        if len(self.__books) > 0:
            book = self.__books[0]
        return book

    def get_last_book(self):
        book = None

        if len(self.__books) > 0:
            book = self.__books[-1]
        return book

    def get_books_by_id(self, id_list):
        # Strip out any ids in id_list that don't represent Book ids in the repository.
        existing_ids = [id for id in id_list if id in self.__books_index]

        # Fetch the Articles.
        books = [self.__books_index[id] for id in existing_ids]
        return books

    def get_book_ids_for_genre(self, genre_name: str):
        # Linear search, to find the first occurrence of a Genre with the name genre_name.
        genre = next((genre for genre in self.__genres if genre.genre_name == genre_name), None)

        # Retrieve the ids of articles associated with the Genre.
        if genre is not None:
            book_ids = [book.book_id for book in genre.genre_books]
        else:
            # No genre with name genre_name, so return an empty list.
            book_ids = list()

        return book_ids

    def get_book_ids_for_author(self, author_name: str):
        # Linear search, to find the first occurrence of a Genre with the name genre_name.
        author = next((author for author in self.__authors if author.full_name == author_name), None)

        # Retrieve the ids of articles associated with the Genre.
        if author is not None:
            book_ids = [book.book_id for book in author.books]
        else:
            # No genre with name genre_name, so return an empty list.
            book_ids = list()

        return book_ids

    def get_book_ids_for_publisher(self, publisher_name: str):
        # Linear search, to find the first occurrence of a Genre with the name genre_name.
        publisher = next((publisher for publisher in self.__publishers if publisher.name == publisher_name), None)

        # Retrieve the ids of articles associated with the Genre.
        if publisher is not None:
            book_ids = [book.book_id for book in publisher.books]
        else:
            # No genre with name genre_name, so return an empty list.
            book_ids = list()

        return book_ids

    def get_release_year_of_previous_book(self, book: Book):
        previous_release_year = None

        try:
            index = self.book_index(book)
            for stored_book in reversed(self.__books[0:index]):
                if stored_book.release_year < book.release_year:
                    previous_release_year = stored_book.release_year
                    break
        except ValueError:
            # No earlier books, so return None.
            pass

        return previous_release_year

    def get_release_year_of_next_book(self, book: Book):
        next_release_year = None

        try:
            index = self.book_index(book)
            for stored_book in self.__books[index + 1:len(self.__books)]:
                if stored_book.release_year > book.release_year:
                    next_release_year = stored_book.release_year
                    break
        except ValueError:
            # No subsequent books, so return None.
            pass

        return next_release_year

    def add_author(self, author: Author):
        self.__authors.append(author)

    def get_authors(self) -> List[Author]:
        return self.__authors

    def add_publisher(self, publisher: Publisher):
        self.__publishers.append(publisher)

    def get_publishers(self) -> List[Publisher]:
        return self.__publishers

    def add_genre(self, genre: Genre):
        self.__genres.append(genre)

    def get_genres(self) -> List[Genre]:
        return self.__genres

    def add_review(self, review: Review):
        # call parent class first, add_review relies on implementation of code common to all derived classes
        super().add_review(review)
        self.__reviews.append(review)

    def get_reviews(self):
        return self.__reviews

    # Helper method to return book index.
    def book_index(self, book: Book):
        index = bisect_left(self.__books, book)
        if index != len(self.__books) and self.__books[index].book_id == book.book_id:
            return index
        raise ValueError


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


def load_authors(data_path: Path, repo: MemoryRepository):
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


def load_books_and_genres(data_path: Path, repo: MemoryRepository, authors):
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


        # Add the Article to the repository.
        repo.add_book(book)

    # Create Genre objects, associate them with Books and add them to the repository.
    for genre_name in genres.keys():
        genre = Genre(genre_name)
        for book_id in genres[genre_name]:
            book = repo.get_book(book_id)
            make_genre_association(book, genre)
        repo.add_genre(genre)


def load_users(data_path: Path, repo: MemoryRepository):
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


def load_reviews(data_path: Path, repo: MemoryRepository, users):
    reviews_filename = str(Path(data_path) / "reviews.csv")
    for data_row in read_csv_file(reviews_filename):
        review = make_review(
            review_text=data_row[2],
            user=users[data_row[0]],
            book=repo.get_book(int(data_row[1])),
            rating=int(data_row[3])
        )
        repo.add_review(review)


def populate(data_path: Path, repo: MemoryRepository):
    # Load authors into the repository.
    authors = load_authors(data_path, repo)

    # Load books and genres into the repository.
    load_books_and_genres(data_path, repo, authors)

    # Load users into the repository.
    users = load_users(data_path, repo)

    # Load comments into the repository.
    load_reviews(data_path, repo, users)
