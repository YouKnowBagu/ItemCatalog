"""App initialization file.  Instantiates app, database, login_manager.  Registers view blueprints.  Defines user_loader callback for LoginManager."""

from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import init_db
from models import Base, Category, User
from views.auth import authModule
from views.categories import categoryModule
from views.items import itemModule
from views.site import siteModule

init_db()
app = Flask(__name__)
login_manager = LoginManager()

login_manager.init_app(app)

csrf = CSRFProtect(app)
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

mycategory = Category(name="banana", description="a banana", user_id=5)
session.add(mycategory)
session.commit()


@login_manager.user_loader
def load_user(userid):
    """User loader for Flask Login. As the user is only stored
    in the session an attempt is made to retrieve the user from the session.
    In case this fails, None is returned.

    Args:
        userid: the user id

    Returns:
        the user object or None in case the user could not be
        retrieved from the session
    """
    print "load_user called: %s" % userid
    user = session.query(User).filter_by(id=str(userid)).first()
    if not user:
        return None
    return user


app.register_blueprint(categoryModule)
app.register_blueprint(itemModule)
app.register_blueprint(authModule)
app.register_blueprint(siteModule)
