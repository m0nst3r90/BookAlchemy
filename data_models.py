import datetime
from typing import Mapping

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from datetime import date

db = SQLAlchemy()

class Author(db.Model):
    """Class for authors"""
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)
    birth_date: Mapped[date] = mapped_column(db.Date)
    date_of_death: Mapped[date | None] = mapped_column(db.Date, nullable=True)
    books: Mapped[list["Book"]] = relationship(back_populates="author", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Author({self.id}, {self.name}, {self.birth_date}, {self.data_of_death})"

    def __str__(self):
        return f"Name: {self.name}, Birth Date: {self.birth_date}"

class Book(db.Model):
    """Class for books"""
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    isbn: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    publication_year: Mapped[int | None] = mapped_column(db.Integer, nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"), nullable=False)
    author: Mapped["Author"] = relationship(back_populates="books")
    rating: Mapped[int | None] = mapped_column(db.Integer)

    @validates("rating")
    def validate_rating(self, key, value):
        if value is not None and not 1 <= value <= 10:
            raise ValueError(f"Invalid rating value: {value}, must be between 1 and 10")
        return value

    def __repr__(self):
        return f"Book({self.id}, {self.isbn}, {self.title}, {self.publication_year})"

    def __str__(self):
        return f"Title: {self.title}, ISBN: {self.isbn}, Publication Year: {self.publication_year}"
