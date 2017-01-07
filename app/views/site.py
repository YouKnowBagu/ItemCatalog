"""Module for basic site related views."""

from flask import Blueprint, request, render_template, flash, g, redirect, url_for
from flask import session as login_session
from sqlalchemy.orm import sessionmaker
from database import session
from flask_login import current_user
from models import Category, User, Item


siteModule = Blueprint('site', __name__)


@siteModule.route('/clearSession')
def clearSession():
    """Clears sticky user sessions, used as a test for development.  Disable on production """
    """Docstring placeholder."""
    login_session.clear()
    # login_session['__invalidate__'] = True
    session.commit()
    return "Session cleared"


@siteModule.route('/cleardb')
def cleardb():
    """Deletes all items from database, used as a test for development.  Disable on production """
    users = session.query(User).all()
    categories = session.query(Category).all()
    items = session.query(Item).all()
    for user in users:
        session.delete(user)
    for category in categories:
        session.delete(category)
    for item in items:
        session.delete(item)
    session.commit()
    return "User DB cleared"


@siteModule.route('/')
def landing():
    """Simple landing with a brief description of the app"""
    return render_template('/home/landing.html')


@siteModule.route('/catalog/')
def home():
    """Displays all categories and items."""
    categories = session.query(Category).all()
    if categories:
        for cat in categories:
            items = session.query(Item).filter_by(category_id=cat.id).all()
            return render_template('home/main.html', categories=categories, items=items)
    else:
        return redirect(url_for('site.landing'))
