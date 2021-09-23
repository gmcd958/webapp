from datetime import datetime
from typing import List, Iterable


class Publisher:

    def __init__(self, publisher_name: str):
        # This makes sure the setter is called here in the initializer/constructor as well.
        self.name = publisher_name
        self.__books: List[Book] = list()

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, publisher_name: str):
        self.__name = "N/A"
        if isinstance(publisher_name, str):
            # Make sure leading and trailing whitespace is removed.
            publisher_name = publisher_name.strip()
            if publisher_name != "":
                self.__name = publisher_name

    @property
    def books(self) -> List['Book']:
        return self.__books

    def add_book(self, book: 'Book'):
        if not isinstance(book, Book):
            return

        if book in self.__books:
            return

        self.__books.append(book)

    def remove_book(self, book: 'Book'):
        if not isinstance(book, Book):
            return

        if book in self.__books:
            self.__books.remove(book)

    def __repr__(self):
        return f'<Publisher {self.name}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.name == self.name

    def __lt__(self, other):
        return self.name < other.name

    def __hash__(self):
        return hash(self.name)


class Author:

    def __init__(self, author_id: int, author_full_name: str):
        if not isinstance(author_id, int):
            raise ValueError

        if author_id < 0:
            raise ValueError

        self.__unique_id = author_id

        # Uses the attribute setter method.
        self.full_name = author_full_name

        # Initialize author colleagues data structure with empty set.
        # We use a set so each unique author is only represented once.
        self.__books: List[Book] = list()

    @property
    def unique_id(self) -> int:
        return self.__unique_id

    @property
    def full_name(self) -> str:
        return self.__full_name

    @full_name.setter
    def full_name(self, author_full_name: str):
        if isinstance(author_full_name, str):
            # make sure leading and trailing whitespace is removed
            author_full_name = author_full_name.strip()
            if author_full_name != "":
                self.__full_name = author_full_name
            else:
                raise ValueError
        else:
            raise ValueError

    @property
    def books(self) -> List['Book']:
        return self.__books

    def add_book(self, book: 'Book'):
        if not isinstance(book, Book):
            return

        if book in self.__books:
            return

        self.__books.append(book)

    def remove_book(self, book: 'Book'):
        if not isinstance(book, Book):
            return

        if book in self.__books:
            self.__books.remove(book)

    def __repr__(self):
        return f'<Author {self.full_name}, author id = {self.unique_id}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.unique_id == other.unique_id

    def __lt__(self, other):
        return self.unique_id < other.unique_id

    def __hash__(self):
        return hash(self.unique_id)


class Book:

    def __init__(self, release_year: int, book_title: str = None, book_id: int = None):

        self.__book_id: int = book_id
        self.__release_year: int = release_year

        # use the attribute setters
        self.title = book_title

        self.__reviews: List[Review] = list()
        self.__genres: List[Genre] = list()

        self.__author = None
        self.__description = None
        self.__publisher = None
        self.__imgurl = None
        self.__ebook = None
        self.__num_pages = None

    @property
    def book_id(self) -> int:
        return self.__book_id

    @property
    def title(self) -> str:
        return self.__title

    @title.setter
    def title(self, book_title: str):
        if isinstance(book_title, str):
            book_title = book_title.strip()
            if book_title != "":
                self.__title = book_title
            else:
                self.__title = None
        else:
            self.__title = None

    @property
    def release_year(self) -> int:
        return self.__release_year

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, description: str):
        if isinstance(description, str):
            self.__description = description.strip()

    @property
    def publisher(self) -> Publisher:
        return self.__publisher

    @publisher.setter
    def publisher(self, publisher: Publisher):
        if isinstance(publisher, Publisher):
            self.__publisher = publisher
        else:
            self.__publisher = None

    @property
    def author(self) -> Author:
        return self.__author

    @author.setter
    def author(self, author: Author):
        if isinstance(author, Author):
            self.__author = author

    @property
    def imgurl(self) -> str:
        return self.__imgurl

    @imgurl.setter
    def imgurl(self, imgurl: str):
        if isinstance(imgurl, str):
            self.__imgurl = imgurl

    @property
    def ebook(self) -> bool:
        return self.__ebook

    @ebook.setter
    def ebook(self, is_ebook: bool):
        if isinstance(is_ebook, bool):
            self.__ebook = is_ebook

    @property
    def num_pages(self) -> int:
        return self.__num_pages

    @num_pages.setter
    def num_pages(self, num_pages: int):
        if isinstance(num_pages, int) and num_pages >= 0:
            self.__num_pages = num_pages

    @property
    def reviews(self) -> Iterable['Review']:
        return iter(self.__reviews)

    @property
    def number_of_reviews(self) -> int:
        return len(self.__reviews)

    def add_review(self, review: 'Review'):
        self.__reviews.append(review)

    @property
    def genres(self) -> Iterable['Genre']:
        return iter(self.__genres)

    @property
    def number_of_genres(self) -> int:
        return len(self.__genres)

    def is_genred_by(self, genre: 'Genre'):
        return genre in self.__genres

    def is_genred(self) -> bool:
        return len(self.__genres) > 0

    def add_genre(self, genre: 'Genre'):
        self.__genres.append(genre)

    def __repr__(self):
        return f'<Book {self.title}, book id = {self.book_id}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.book_id == other.book_id

    def __lt__(self, other):
        return self.book_id < other.book_id #  & self.__release_year < other.release_year

    def __hash__(self):
        return hash(self.book_id)


class Review:

    def __init__(self, book: Book, review_text: str, user: 'User', rating: int):
        if isinstance(book, Book):
            self.__book = book
        else:
            self.__book = None

        if isinstance(review_text, str):
            self.__review_text = review_text.strip()
        else:
            self.__review_text = "N/A"

        if isinstance(user, User):
            self.__user = user
        else:
            self.__user = None

        if isinstance(rating, int) and 1 <= rating <= 5:
            self.__rating = rating
        else:
            raise ValueError

        self.__timestamp = datetime.now()

    @property
    def book(self) -> Book:
        return self.__book

    @property
    def review_text(self) -> str:
        return self.__review_text

    @property
    def user(self) -> 'User':
        return self.__user

    @property
    def rating(self) -> int:
        return self.__rating

    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return other.book == self.book and other.review_text == self.review_text \
               and other.rating == self.rating and other.timestamp == self.timestamp

    def __repr__(self):
        return f'<Review of book {self.book}, text = {self.review_text}, rating = {self.rating}, timestamp = {self.timestamp}>'


class User:

    def __init__(self, user_name: str, password: str):
        if user_name == "" or not isinstance(user_name, str):
            self.__user_name = None
        else:
            self.__user_name = user_name.strip().lower()

        if password == "" or not isinstance(password, str) or len(password) < 7:
            self.__password = None
        else:
            self.__password = password

        self.__read_books = []
        self.__reviews = []
        self.__pages_read = 0

    @property
    def user_name(self) -> str:
        return self.__user_name

    @property
    def password(self) -> str:
        return self.__password

    @property
    def read_books(self) -> List[Book]:
        return self.__read_books

    @property
    def reviews(self) -> List[Review]:
        return self.__reviews

    @property
    def pages_read(self) -> int:
        return self.__pages_read

    def read_a_book(self, book: Book):
        if isinstance(book, Book):
            self.__read_books.append(book)
            if book.num_pages is not None:
                self.__pages_read += book.num_pages

    def add_review(self, review: Review):
        if isinstance(review, Review):
            # Review objects are in practice always considered different due to their timestamp.
            self.__reviews.append(review)

    def __repr__(self):
        return f'{self.user_name}'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.user_name == self.user_name

    def __lt__(self, other):
        return self.user_name < other.user_name

    def __hash__(self):
        return hash(self.user_name)


class Genre:
    def __init__(self, genre_name: str):
        self.__genre_name: str = genre_name
        self.__genre_books: List[Book] = list()

    @property
    def genre_name(self) -> str:
        return self.__genre_name

    @property
    def genre_books(self) -> Iterable[Book]:
        return iter(self.__genre_books)

    @property
    def number_of_genre_books(self) -> int:
        return len(self.__genre_books)

    def is_applied_to(self, book: Book) -> bool:
        return book in self.__genre_books

    def add_book(self, book: Book):
        self.__genre_books.append(book)

    def __eq__(self, other):
        if not isinstance(other, Genre):
            return False
        return other.genre_name == self.genre_name


class BooksInventory:

    def __init__(self):
        self.__books = {}
        self.__prices = {}
        self.__stock_count = {}

    def add_book(self, book: Book, price: int, nr_books_in_stock: int):
        self.__books[book.book_id] = book
        self.__prices[book.book_id] = price
        self.__stock_count[book.book_id] = nr_books_in_stock

    def remove_book(self, book_id: int):
        self.__books.pop(book_id)
        self.__prices.pop(book_id)
        self.__stock_count.pop(book_id)

    def find_book(self, book_id: int):
        if book_id in self.__books.keys():
            return self.__books[book_id]
        return None

    def find_price(self, book_id: int):
        if book_id in self.__books.keys():
            return self.__prices[book_id]
        return None

    def find_stock_count(self, book_id: int):
        if book_id in self.__books.keys():
            return self.__stock_count[book_id]
        return None

    def search_book_by_title(self, book_title: str):
        for book_id in self.__books.keys():
            if self.__books[book_id].title == book_title:
                return self.__books[book_id]
        return None


class ModelException(Exception):
    pass


def make_genre_association(book: Book, genre: Genre):
    if genre.is_applied_to(book):
        raise ModelException(f'Genre {genre.genre_name} already applied to Book "{book.title}"')
    else:
        book.add_genre(genre)
        genre.add_book(book)


def make_review(review_text: str, user: User, book: Book, rating: int):
    review = Review(book, review_text, user, rating)
    user.add_review(review)
    book.add_review(review)

    return review
