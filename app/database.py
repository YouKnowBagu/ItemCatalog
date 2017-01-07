from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('sqlite:///catalog.db')
DBSession = sessionmaker(bind=engine)
session = DBSession()


def init_db():
    from models import Base, User, Category, Item
    engine = create_engine('sqlite:///catalog.db')
    Base.metadata.create_all(engine)

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    session.add(User(name="Q", email="queue@queue.com"))
    session.add(User(name="Joe", email='joe@joe.com'))
    session.add(User(name="Sal", email='sal@sal.com'))
    session.add(User(name="Murr", email='murr@murr.com'))
    session.add(User(name="Sean", email='sean@sean.com'))
    session.add(Category(name="Python"))
    session.add(
        Item(
            name="Computer",
            description="Really cool awesome computer man.",
            category_id=1))
    session.add(Category(name="Flask"))
    session.add(
        Item(
            name="Great Gatsby",
            description="Holy cow read this book its great",
            category_id=2))
    session.add(Category(name="Google App Engine"))
    session.add(
        Item(
            name="Baseball",
            description="WTF baeballs are the best",
            category_id=3))
    session.add(Category(name="Jinja2"))
    session.add(
        Item(
            name="Assassin's Creed",
            description="it's a video game lol",
            category_id=4))
    session.add(Category(name="SQLAlchemy"))
    session.add(
        Item(
            name="The Big Lebowski", description="Abide", category_id=5))
    session.add(Category(name="PostgreSQL"))
    session.add(Category(name="SQLite"))
    session.add(Category(name="PsycoPG2"))
    session.add(Category(name="WebApp2"))
    session.add(Category(name="Cloud Datastore"))

    session.commit()
