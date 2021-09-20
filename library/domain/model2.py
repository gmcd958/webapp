from datetime import date, datetime
from typing import List, Iterable


class User:
    def __init__(self, user_name: str, password: str):
        self.__user_name: str = user_name
        self.__password: str = password
        self.__comments: List[Comment] = list()

    @property
    def user_name(self) -> str:
        return self.__user_name

    @property
    def password(self) -> str:
        return self.__password

    @property
    def comments(self) -> Iterable['Comment']:
        return iter(self.__comments)

    def add_comment(self, comment: 'Comment'):
        self.__comments.append(comment)

    def __repr__(self) -> str:
        return f'<User {self.__user_name} {self.__password}>'

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return other.user_name == self.user_name


class Comment:
    def __init__(self, user: User, article: 'Article', comment: str, timestamp: datetime):
        self.__user: User = user
        self.__article: Article = article
        self.__comment: str = comment
        self.__timestamp: datetime = timestamp

    @property
    def user(self) -> User:
        return self.__user

    @property
    def article(self) -> 'Article':
        return self.__article

    @property
    def comment(self) -> str:
        return self.__comment

    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

    def __eq__(self, other):
        if not isinstance(other, Comment):
            return False
        return other.user == self.user and other.article == self.article and \
               other.comment == self.comment and other.timestamp == self.timestamp



class Article:
    def __init__(self, date: date, title: str, first_paragraph: str, hyperlink: str, image_hyperlink: str, id: int = None):
        self.__id: int = id
        self.__date: date = date
        self.__title: str = title
        self.__first_paragraph: str = first_paragraph
        self.__hyperlink: str = hyperlink
        self.__image_hyperlink: str = image_hyperlink
        self.__comments: List[Comment] = list()
        self.__tags: List[Tag] = list()

    @property
    def id(self) -> int:
        return self.__id

    @property
    def date(self) -> date:
        return self.__date

    @property
    def title(self) -> str:
        return self.__title

    @property
    def first_paragraph(self) -> str:
        return self.__first_paragraph

    @property
    def hyperlink(self) -> str:
        return self.__hyperlink

    @property
    def image_hyperlink(self) -> str:
        return self.__image_hyperlink

    @property
    def comments(self) -> Iterable[Comment]:
        return iter(self.__comments)

    @property
    def number_of_comments(self) -> int:
        return len(self.__comments)

    @property
    def number_of_tags(self) -> int:
        return len(self.__tags)

    @property
    def tags(self) -> Iterable['Tag']:
        return iter(self.__tags)

    def is_tagged_by(self, tag: 'Tag'):
        return tag in self.__tags

    def is_tagged(self) -> bool:
        return len(self.__tags) > 0

    def add_comment(self, comment: Comment):
        self.__comments.append(comment)

    def add_tag(self, tag: 'Tag'):
        self.__tags.append(tag)

    def __repr__(self):
        return f'<Article {self.date.isoformat()} {self.title}>'

    def __eq__(self, other):
        if not isinstance(other, Article):
            return False
        return (
                other.date == self.date and
                other.title == self.title and
                other.first_paragraph == self.first_paragraph and
                other.hyperlink == self.hyperlink and
                other.image_hyperlink == self.image_hyperlink
        )

    def __lt__(self, other):
        return self.date < other.date


class Tag:
    def __init__(self, tag_name: str):
        self.__tag_name: str = tag_name
        self.__tagged_articles: List[Article] = list()

    @property
    def tag_name(self) -> str:
        return self.__tag_name

    @property
    def tagged_articles(self) -> Iterable[Article]:
        return iter(self.__tagged_articles)

    @property
    def number_of_tagged_articles(self) -> int:
        return len(self.__tagged_articles)

    def is_applied_to(self, article: Article) -> bool:
        return article in self.__tagged_articles

    def add_article(self, article: Article):
        self.__tagged_articles.append(article)

    def __eq__(self, other):
        if not isinstance(other, Tag):
            return False
        return other.tag_name == self.tag_name


class ModelException(Exception):
    pass


def make_comment(comment_text: str, user: User, article: Article, timestamp: datetime = datetime.today()):
    comment = Comment(user, article, comment_text, timestamp)
    user.add_comment(comment)
    article.add_comment(comment)

    return comment


def make_tag_association(article: Article, tag: Tag):
    if tag.is_applied_to(article):
        raise ModelException(f'Tag {tag.tag_name} already applied to Article "{article.title}"')

    article.add_tag(tag)
    tag.add_article(article)
