from typing import List

from bisect import bisect_left, insort_left


from library.adapters.repository import AbstractRepository
from library.domain.model import Publisher, Author, Book, Review, User, Genre

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
