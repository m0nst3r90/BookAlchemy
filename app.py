import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

from data_models import db, Author, Book

from Ai_handling import get_recommendation, ai_available
from setup_data import setup_database
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.config["SECRET_KEY"] = "secret"
db.init_app(app)

@app.route('/')
def index():
    sort_by = request.args.get("sort", "title")
    search = request.args.get("search", "")
    query = db.select(Book)

    if search:
        query = query.where(
            Book.title.like(f"%{search}%")
        )

    if sort_by == "title":
        query = query.order_by(Book.title)

    elif sort_by == "publication_year":
        query = query.order_by(Book.publication_year)

    elif sort_by == "isbn":
        query = query.order_by(Book.isbn)

    elif sort_by == "author":
        query = (
            query
            .join(Book.author)
            .order_by(Author.name)
        )

    books = db.session.scalars(query).all()
    return render_template("home.html", books=books, ai_available=ai_available())

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'GET':
        authors = db.session.scalars(db.select(Author).order_by(Author.name)).all()
        return render_template("add_book.html", authors=authors)

    book_title = request.form.get("book_title")
    book_isbn = request.form.get("book_isbn")
    book_publication_year = request.form.get("book_publication_year")
    book_author_id = request.form.get("book_author_id")

    new_book = Book(
        isbn=book_isbn,
        title=book_title,
        publication_year=book_publication_year,
        author_id=book_author_id
    )

    db.session.add(new_book)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Ein Buch mit dieser ISBN existiert bereits.", "error")
        return redirect(url_for("add_book"))

    flash(f'Buch "{book_title}" wurde erfolgreich hinzugefügt.', "success")
    return redirect(url_for("index"))

@app.route("/book/<int:book_id>")
def book_detail(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        return "Buch nicht gefunden", 404

    return render_template("detail_book.html", book=book)

@app.route("/book/<int:book_id>/rate", methods=["POST"])
def rate_book(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        flash("Buch wurde nicht gefunden.", "error")
        return redirect(url_for("index"))

    rating = request.form.get("rating")
    try:
        book.rating = int(rating)
        db.session.commit()

        flash("Bewertung wurde gespeichert.", "success")
    except (ValueError, TypeError):
        db.session.rollback()
        flash("Bewertung muss zwischen 1 und 10 liegen.", "error")

    return redirect(url_for("book_detail", book_id=book.id))

@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = db.session.query(Book).get(book_id)
    if book:
        author_id = book.author_id
        db.session.delete(book)
        db.session.flush()

        books_left = db.session.scalar(
            db.select(Book).where(Book.author_id == author_id).limit(1)
        )
        if books_left is None:
            author = db.session.get(Author, author_id)
            if author:
                author_name = author.name
                db.session.delete(author)
                flash(f"Autor: {author_name} wurde erfolgreich gelöscht.", "success")

        db.session.commit()
        flash("Buch wurde erfolgreich gelöscht.", "success")

    return redirect(url_for("index"))

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'GET':
        return render_template("add_author.html")

    author_name = request.form.get("author_name")
    author_birth_date = request.form.get("author_birth_date")
    birth_date = datetime.strptime(author_birth_date, "%Y-%m-%d").date()
    author_date_of_death = request.form.get("author_date_of_death")
    if author_date_of_death:
        death_date = datetime.strptime(author_date_of_death, "%Y-%m-%d").date()
    else:
        death_date = None
    new_author = Author(name=author_name, birth_date=birth_date, date_of_death=death_date)
    db.session.add(new_author)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Ein Autor mit diesem Namen existiert bereits.", "error")
        return redirect(url_for("add_author"))

    flash(f'Autor "{author_name}" wurde erfolgreich hinzugefügt.', "success")
    return redirect(url_for("index"))

@app.route("/author/<int:author_id>")
def author_detail(author_id):
    author = db.session.get(Author, author_id)

    if author is None:
        return "Autor nicht gefunden", 404

    return render_template(
        "author_detail.html",
        author=author
    )

@app.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    author = db.session.get(Author, author_id)
    if author is None:
        flash("Author nicht gefunden", "error")
        return redirect(url_for("index"))

    author_name = author.name
    db.session.delete(author)
    db.session.commit()
    flash(f"Author {author_name} erfolgreich gelöscht!", "success")

    return redirect(url_for("index"))

@app.route('/recommendation', methods=['GET'])
def recommendation():
    if not ai_available():
        flash("Kein Gemini API-Key vorhanden. KI-Buchempfehlungen sind daher nicht verfügbar.", "error")
        return redirect(url_for("index"))

    data = get_books()
    if not data:
        flash("Es sind keine Bücher vorhanden, aus denen die KI wählen könnte.", "error")
        return redirect(url_for("index"))

    recommendation_data = get_recommendation(data)
    if recommendation_data is None:
        flash("Die KI konnte gerade keine Empfehlung erstellen.", "error")
        return redirect(url_for("index"))

    book_id = recommendation_data["book_id"]
    recommendation_text = recommendation_data["text"]
    if not book_id or not recommendation_text:
        flash("Die KI hat keine gültige Empfehlung geliefert.", "error")
        return redirect(url_for("index"))

    book = db.session.get(Book, book_id)
    if book is None:
        flash("Die KI hat ein unbekanntes Buch ausgewählt.", "error")
        return redirect(url_for("index"))

    flash(recommendation_text, "recommendation")
    return redirect(url_for("book_detail", book_id=book.id))

def get_books():
    books = db.session.scalars(db.select(Book)).all()

    data = []

    for book in books:
        book_data = {
            "id": book.id,
            "title": book.title,
            "author": book.author.name,
            "publication_year": book.publication_year
        }

        if book.rating is not None:
            book_data["rating"] = book.rating

        data.append(book_data)

    return data


if __name__ == '__main__':
    # Reset database to default every start
    setup_database(app)
    app.run(debug=False, host="0.0.0.0", port=5002)