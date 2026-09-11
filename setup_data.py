from datetime import date

from data_models import db, Author, Book

def setup_database(app):
    """Reroll Database"""
    with app.app_context():
        db.drop_all()
        db.create_all()

        orwell = Author(
            name="George Orwell",
            birth_date=date(1903, 6, 25),
            date_of_death=date(1950, 1, 21)
        )

        tolkien = Author(
            name="J. R. R. Tolkien",
            birth_date=date(1892, 1, 3),
            date_of_death=date(1973, 9, 2)
        )

        rowling = Author(
            name="J. K. Rowling",
            birth_date=date(1965, 7, 31)
        )

        king = Author(
            name="Stephen King",
            birth_date=date(1947, 9, 21)
        )

        atwood = Author(
            name="Margaret Atwood",
            birth_date=date(1939, 11, 18)
        )

        austen = Author(
            name="Jane Austen",
            birth_date=date(1775, 12, 16),
            date_of_death=date(1817, 7, 18)
        )

        camus = Author(
            name="Albert Camus",
            birth_date=date(1913, 11, 7),
            date_of_death=date(1960, 1, 4)
        )

        kafka = Author(
            name="Franz Kafka",
            birth_date=date(1883, 7, 3),
            date_of_death=date(1924, 6, 3)
        )

        marquez = Author(
            name="Gabriel García Márquez",
            birth_date=date(1927, 3, 6),
            date_of_death=date(2014, 4, 17)
        )

        murakami = Author(
            name="Haruki Murakami",
            birth_date=date(1949, 1, 12)
        )

        books = [

            Book(
                title="1984",
                isbn="9780451524935",
                publication_year=1949,
                author=orwell
            ),

            Book(
                title="The Hobbit",
                isbn="9780547928227",
                publication_year=1937,
                author=tolkien
            ),

            Book(
                title="Harry Potter and the Philosopher's Stone",
                isbn="9780747532699",
                publication_year=1997,
                author=rowling
            ),

            Book(
                title="The Shining",
                isbn="9780307743657",
                publication_year=1977,
                author=king
            ),

            Book(
                title="The Handmaid's Tale",
                isbn="9780385490818",
                publication_year=1985,
                author=atwood
            ),

            Book(
                title="Pride and Prejudice",
                isbn="9780141439518",
                publication_year=1813,
                author=austen
            ),

            Book(
                title="The Stranger",
                isbn="9780679720201",
                publication_year=1942,
                author=camus
            ),

            Book(
                title="The Trial",
                isbn="9780805204162",
                publication_year=1925,
                author=kafka
            ),

            Book(
                title="One Hundred Years of Solitude",
                isbn="9780060883287",
                publication_year=1967,
                author=marquez
            ),

            Book(
                title="Norwegian Wood",
                isbn="9780375704024",
                publication_year=1987,
                author=murakami
            )
        ]

        db.session.add_all(books)
        db.session.commit()
        print("Datenbank zurückgesetzt.")
