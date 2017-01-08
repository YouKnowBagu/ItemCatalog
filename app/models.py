import datetime

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, LargeBinary,
                        String, Text, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class User(Base):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
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
    items = relationship('Item')
    created = Column('Created', DateTime())

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'created': self.created,
            'user': self.user_id
        }


class Item(Base):

    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created = Column('Created', DateTime())
    category_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'category': self.category_id,
            'user': self.user_id,
            'name': self.name,
            'description': self.description,
            'id': self.id,
        }
