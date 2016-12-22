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
    created = Column('Created', DateTime())
    picture = Column(Text, nullable = True)
    picture_data = Column(LargeBinary, nullable = True)

class Category(Base):

    __tablename__ = "category"

    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False)
    description = Column(Text, nullable = True)
    created = Column('Created', DateTime())
    picture = Column(Text, nullable = True)
    picture_data = Column(LargeBinary, nullable = True)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)


class Item(Base):

    __tablename__ = "item"

    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False)
    description = Column(Text, nullable = True)
    created = Column('Created', DateTime())
    picture = Column(Text, nullable = True)
    picture_data = Column(LargeBinary, nullable = True)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)
    category_id = Column(Integer, ForeignKey("category.id"))
    category = relationship(Category)

if __name__ == '__main__':
    engine = create_engine('sqlite:///catalog.db')
    Base.metadata.create_all(engine)

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    session.add(User(name="Q"))
    session.add(User(name="Joe"))
    session.add(User(name="Sal"))
    session.add(User(name="Murr"))
    session.add(User(name="Sean"))
    session.add(Category(name="Electronics"))
    session.add(Item(name="Computer"))
    session.add(Category(name="Books"))
    session.add(Item(name="Great Gatsby"))
    session.add(Category(name="Sports"))
    session.add(Item(name="Baseball"))
    session.add(Category(name="Videogames"))
    session.add(Item(name="Assassin's Creed"))
    session.add(Category(name="Movies"))
    session.add(Item(name="The Big Lebowski"))

    session.commit()