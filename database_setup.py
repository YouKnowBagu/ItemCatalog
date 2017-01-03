import sys

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import datetime
from flask_login import UserMixin

Base = declarative_base()
# DBSession = sessionmaker(bind=engine)
# session = DBSession()


class User(Base):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(
        255), nullable=False)
    email = Column(String, nullable=False)
    picture = Column(Text, nullable=True)
    picture_data = Column(LargeBinary, nullable=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

        
class Category(Base):

    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    created = Column('Created', DateTime())

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description
        }


class Item(Base):

    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    created = Column('Created', DateTime())
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
        }

if __name__ == '__main__':
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
    session.add(Item(name="Computer",
                     description="Really cool awesome computer man.", category_id=1))
    session.add(Category(name="Flask"))
    session.add(Item(name="Great Gatsby",
                     description="Holy cow read this book its great", category_id=2))
    session.add(Category(name="Google App Engine"))
    session.add(
        Item(name="Baseball", description="WTF baeballs are the best", category_id=3))
    session.add(Category(name="Jinja2"))
    session.add(Item(name="Assassin's Creed",
                     description="it's a video game lol", category_id=4))
    session.add(Category(name="SQLAlchemy"))
    session.add(Item(name="The Big Lebowski",
                     description="Abide", category_id=5))
    session.add(Category(name="PostgreSQL"))
    session.add(Category(name="SQLite"))
    session.add(Category(name="PsycoPG2"))
    session.add(Category(name="WebApp2"))
    session.add(Category(name="Cloud Datastore"))


    session.commit()
