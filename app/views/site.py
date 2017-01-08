"""Module for basic site related views."""

from flask import session as login_session
from flask import Blueprint, g, redirect, render_template, request, url_for

from app.database import session
from app.models import Category, Item, User

siteModule = Blueprint('site', __name__)


@siteModule.route('/clearSession')
def clearSession():
    """Clear sticky user sessions, used as a test for development.  Disable on production."""
    login_session.clear()
    session.commit()
    return "Session cleared"


@siteModule.route('/cleardb')
def cleardb():
    """Delete all items from database, used as a test for development. Disable on production."""
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
    """Simple landing with a brief description of the appself."""
    return render_template('/home/landing.html')


@siteModule.route('/catalog/')
def home():
    """Displays all categories and items."""
    categories = session.query(Category).all()
    if categories:
        for cat in categories:
            items = session.query(Item).filter_by(category_id=cat.id).all()
            return render_template(
                'home/main.html', categories=categories, items=items)
    else:
        return redirect(url_for('site.landing'))
