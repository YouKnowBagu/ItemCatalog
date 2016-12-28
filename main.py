"""Docstring placeholder."""

import json
import random
import string

import httplib2
import requests
from flask import session as login_session
from flask import (Flask, flash, jsonify, make_response, redirect,
                   render_template, request, url_for)
from oauth2client.client import FlowExchangeError, flow_from_clientsecrets
from sqlalchemy import asc, create_engine, desc
from sqlalchemy.orm import scoped_session, sessionmaker
from database_setup import Base, Category, Item, User

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']
APPLICATION_NAME = "Catalog"
app.config['SQLALCHEMY_ECHO'] = True


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Base.query = DBSession.query_property()

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
    return render_template('main.html', categories=categories, items=items)


@app.route('/login')
def showLogin():
    """Docstring placeholder."""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


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
    return "Session cleared"
#
#
# @app.route('/item/<int:category_id>/tester', methods=['GET', 'POST'])
# def dataTest(category_id):
#     editedcategory = session.query(Category).filter_by(id=category_id).one()
#     if request.method == 'POST':
#         if request.form['name']:
#             editedcategory.name = request.form['name']
#             session.commit()
#             flash('Catalog Successfully Edited %s' % editedcategory.name)
#             return redirect(url_for('home'))
#         else:
#             return redirect(url_for('dataTest', category_id=category_id))
#     else:
#         return render_template('editCategory.html', category=editedcategory)


@app.route('/category/new', methods=['GET', 'POST'])
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


@app.route('/category/edit/<int:category_id>', methods = ['GET', 'POST'])
def editCategory(category_id):
    editedcategory = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedcategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editedcategory.name)
            return redirect(url_for('home'))
        else:
            return redirect(url_for('editCategory', category_id=category_id))
    else:
        return render_template('editCategory.html', category=editedcategory)


@app.route('/category/<string:category_name>/delete', methods=['GET', 'POST'])
def deleteCategory(category_name):
    category = session.query(Category).filter_by(name = category_name).one()
    if request.method == 'GET':
        return render_template('deleteCategory.html', category=category)
    else:
        session.delete(category)
        session.commit()
        flash("The category '%s' has been removed." % category.name, "success")
        return redirect(url_for('home'))


@app.route('/<string:category_name>/items')
@app.route('/catalog/<int:category_id>')
def categoryItems(category_name):
    category = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Item).filter_by(category_name=category_name).all()
    return render_template('categoryview.html', category=category, items=items)


@app.route('/items/new', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = Item(name=request.form['name'], description=request.form[
                       'description'])
        session.add(newItem)
        session.commit()
        flash('New Item, %s, successfully created.' % (newItem.name))
        return redirect(url_for('home'))
    else:
        return render_template('newitem.html')


@app.route('/item/edit/<string:category_name>/<int:item_id>',
           methods=['GET', 'POST'])
def editItem(category_name, item_id):
    category = session.query(Category).filter_by(name = category_name)
    editeditem = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editeditem.name = request.form['name']
            session.commit()
            flash('Item Successfully Edited %s' % editeditem.name)
            return redirect(url_for('home'))
        else:
            return redirect(url_for('editItem', category_name = category_name, item_id=item_id))
    else:
        return render_template('editItem.html', category_name = category_name, item=editeditem)


@app.route('/item/<string:item_name>/delete', methods=['GET', 'POST'])
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


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
