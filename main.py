"""Docstring placeholder."""
# TODO Local authorization
# TODO Add category button on home postmessage
# TODO Login/logout design
# TODO Search?
# TODO
import json
import random
import string
from jinja2 import Template
import httplib2
import requests
from flask import session as login_session
from flask import (Flask, flash, g, jsonify, make_response,
                   redirect, render_template, request, url_for)
from logindecorator import login_required
from flask_login import LoginManager, login_user, logout_user, login_required
from oauth2client.client import FlowExchangeError, flow_from_clientsecrets
from sqlalchemy import asc, create_engine, desc
from sqlalchemy.orm import scoped_session, sessionmaker
from database_setup import Base, Category, Item, User
from flask.ext.github import GitHub

login_manager = LoginManager()

app = Flask(__name__)
app.config['GITHUB_CLIENT_ID'] = '9dcbd5554b3b28cc265a'
app.config['GITHUB_CLIENT_SECRET'] = 'ff49357da715ce0996913bcc4493c3cfe9ab2b71'

# # For GitHub Enterprise
# app.config['GITHUB_BASE_URL'] = 'https://HOSTNAME/api/v3/'
# app.config['GITHUB_AUTH_URL'] = 'https://HOSTNAME/login/oauth/'
github_callback_url = "http://localhost:8080/github-callback"

github = GitHub(app)
login_manager.init_app(app)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']
APPLICATION_NAME = "Catalog"
app.config['SQLALCHEMY_ECHO'] = True


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Base.query = DBSession.query_property()

# blueprints: category, item, user

# routes:
# / home - home
# /catalog - home
# /catalog/<string:category_name> - view all items of a specific category
# /catalog/<string_category_name>/<string:item_id> - detail item view
# /category/new -create new Category
# /category/<string:category_name>/edit - edit category
# /category/<string:category_name>/delete - delete category
# /item/new - new items
# /item/<string:item_name>/edit - edit item
# /item/<string:item_name>/delete - delete item
# /login - login via google
# /gdisconnect - delete user session


@app.route('/')
@app.route('/catalog/')
def home():
    """Docstring placeholder."""
    categories = session.query(Category).all()
    items = session.query(Item).order_by(desc(Item.created)).limit(10).all()
    provider = login_session['provider']
    return render_template('index.html', categories=categories, items=items)


@app.route('/login')
def showLogin():
    """Docstring placeholder."""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token


@app.route('/github-callback')
@github.authorized_handler
def authorized(access_token):
    next_url = request.args.get('next') or url_for('home')
    if access_token is None:
        return redirect(url_for('home'))

    user = session.query(User).filter_by(
        github_access_token=access_token).first()
    if user is None:
        user = User(name = "", email="generic@generic.com", github_access_token=access_token)
        session.add(user)
    user.github_access_token = access_token
    session.commit()
    login_session['user_id'] = user.id
    login_session['provider'] = 'github'
    return redirect(next_url)


# @app.route('/login')
# def login():
#         # send user back to the source page
#     uri = github_callback_url + "?next=" + request.referrer
#     return github.authorize(redirect_uri=uri)
#     # if session.get('user_id', None) is None:
#     #     return github.authorize()
#     # else:
#     #     flash('User is already logged in')
#     #     return redirect(url_for('showCatalog'))


@app.route('/logout')
def logout():
    login_session.pop('user_id', None)
    return redirect(url_for('home'))


# @app.before_request
# def before_request():
# 	g.user = None
# 	if 'user_id' in session:
# 		g.user = User.query.get(session['user_id'])
# 		g.user.name = github.get('user')["name"]
# 		g.user.avatar = github.get('user')["avatar_url"]
# 		db_session.add(g.user)
# 		db_session.commit()

@app.route('/user')
def user():
    return str(github.get('user'))

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Docstring placeholder."""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    print result
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
        login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """Docstring placeholder."""
    access_token = login_session['access_token']
    print 'In gdisconnect access token is ' + access_token
    print 'User name is:'
    print login_session['username']
    if access_token is None:
        print 'Access token is none'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=' + access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print result
    print result['status']

    if result['status'] == '200':
        # Reset session
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/clearSession')
def clearSession():
    """Docstring placeholder."""
    login_session.clear()
    login_session['__invalidate__'] = True
    session.commit()
    return "Session cleared"


@app.route('/cleardb')
def cleardb():
    """Docstring placeholder."""
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


@app.route('/test', methods=['GET', 'POST'])
def dataTest():
    if request.method == 'GET':
        sesh = login_session
        for i in login_session:
            print i


@app.route('/category/new', methods=['GET', 'POST'])
@login_required
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)
        flash('New category successfully created')
        session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('newCategory.html')


@app.route('/category/<string:category_name>/edit', methods=['GET', 'POST'])
@login_required
def editCategory(category_name):
    editedcategory = session.query(
        Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        if request.form['name']:
            editedcategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editedcategory.name)
            return redirect(url_for('home'))
        else:
            return redirect(url_for('editCategory', category_name=category_name))
    else:
        return render_template('editCategory.html', category=editedcategory)


@app.route('/category/<string:category_name>/delete', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    if request.method == 'GET':
        return render_template('deleteCategory.html', category=category)
    else:
        session.delete(category)
        session.commit()
        flash("The category '%s' has been removed." % category.name, "success")
        return redirect(url_for('home'))


@app.route('/<string:category_name>', methods=['GET'])
def viewCategory(category_name):
    category = session.query(Category).filter_by(name=category_name).first()
    # items = session.query(Item).filter_by(category_id=Item.category_id).all()
    if request.method == 'GET':
        return render_template('category.html', category=category)


# @app.route('/<string:category_name>/<string:item_name>', methods=['GET'])
# def viewItem(category_name, item_name):
#     category = session.query(Category).filter_by(name=category_name).first()
#     item = session.query(Item).filter_by(
#         name=item_name, category_id=category.id).first()
#     if request.method == 'GET' and category.id == item.category.id:
#         return render_template('item.html', category=category, item=item)


@app.route('/item/new', methods=['GET', 'POST'])
@login_required
def newItem():
    if request.method == 'POST':
        newItem = Item(name=request.form['name'], description=request.form[
                       'description'])
        session.add(newItem)
        session.commit()
        flash('New Item, %s, successfully created.' % (newItem.name))
        return redirect(url_for('home'))
    else:
        return render_template('newitem.html')


@app.route('/item/<string:item_name>/edit',
           methods=['GET', 'POST'])
@login_required
def editItem(item_name):
    editeditem = session.query(Item).filter_by(name=item_name).one()
    if request.method == 'POST':
        if request.form['name']:
            editeditem.name = request.form['name']
            session.commit()
            flash('Item Successfully Edited %s' % editeditem.name)
            return redirect(url_for('home'))
        else:
            return redirect(url_for('editItem', item_name=item_name))
    else:
        return render_template('editItem.html', item=editeditem)


@app.route('/item/<string:item_name>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(item_name):
    """Find and delete an item"""
    item = session.query(Item).filter_by(name=item_name).one()
    if request.method == 'GET':
        return render_template('deleteItem.html', item=item)
    else:
        session.delete(item)
        session.commit()
        flash("The item '%s' has been removed." % item.name, "success")
        return redirect(url_for('home'))


@login_manager.user_loader
def load_user(userid):
    """User loader for Flask Login. As the user is only stored
    in the session an attempt is made to retrieve the user from the session.
    In case this fails, None is returned.

    Args:
        userid: the user id

    Returns:
        the user object or None in case the user could not be retrieved from the session
    """
    try:
        print "load_user called: %s" % userid
        user = session.query(User).filter_by(id=str(userid)).first()

        if not user:
            return None

        return user
    except:
        return None


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Disconnect based on provider


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showRestaurants'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showRestaurants'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
