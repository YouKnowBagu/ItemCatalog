import sys

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import datetime

Base = declarative_base()
# DBSession = sessionmaker(bind=engine)
# session = DBSession()

class User(Base):

    __tablename__ = "user"

    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False)
    email = Column(String, nullable = False)
    picture = Column(Text, nullable = True)
    picture_data = Column(LargeBinary, nullable = True)

class Category(Base):

    __tablename__ = "category"

    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    created = Column('Created', DateTime())

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'name': self.name,
            'id': self.id,
        }

class Item(Base):

    __tablename__ = "item"

    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False)
    description = Column(Text, nullable = True)
    created = Column('Created', DateTime())
    price = Column(String(8))
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
            'price': self.price,
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
    session.add(Category(name="Electronics"))
    session.add(Item(name="Computer", category_id=1))
    session.add(Category(name="Books"))
    session.add(Item(name="Great Gatsby", category_id=2))
    session.add(Category(name="Sports"))
    session.add(Item(name="Baseball", category_id=3))
    session.add(Category(name="Videogames"))
    session.add(Item(name="Assassin's Creed",category_id=4))
    session.add(Category(name="Movies"))
    session.add(Item(name="The Big Lebowski", category_id=5))

    session.commit()