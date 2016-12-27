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
# show all
# /
# /catalog/
# /catalog/categories
# /catalog/categories/new
# /catalog/category/<int: category_id>/edit
# /catalog/category/<int: category_id>/delete
# /catalog/<int: category_id>/items
# and
# /catalog/<int: category_id>/
# add item
# /catalog/<int: category_id>/items/new
# /catalog/<int: category_id>/item/<int: item_id>/edit
# /catalog/<int: category_id>/item/<int: item_id>/delete
# /catalog/register
# /catalog/login
# /catalog/logout


@app.route('/')
@app.route('/catalog/')
def home():
    """Docstring placeholder."""
    output = ''
    # output += str(login_session[:])
    print output
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
    """DOcstring placeholder."""
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


# REVIEW: THIS EDIT CODE IS WORKING
@app.route('/item/<int:category_id>/tester', methods=['GET', 'POST'])
def dataTest(category_id):
    editedcategory = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedcategory.name = request.form['name']
            flash('Catalog Successfully Edited %s' % editedcategory.name)
            return redirect(url_for('home'))
        else:
            return redirect(url_for('dataTest', category_id=category_id))
    else:
        return render_template('editCategory.html', category=editedcategory)





@app.route('/catalog/categories/new', methods=['GET', 'POST'])
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

# REVIEW: FILL IN WORKING EDIT CODE HERE
# @app.route('/category/<int:category_id>/edit', methods = ['GET', 'POST'])
# def editCategory(category_id):


@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    # item = session.query(Item).get(item_id)
    if request.method == 'GET':
        return render_template('deleteCategory.html', category=category)
    else:
        session.delete(category)
        session.commit()
        flash("The category '%s' has been removed." % category.name, "success")
        return redirect(url_for('home'))


@app.route('/catalog/<int:category_id>/items')
@app.route('/catalog/<int:category_id>')
def categoryItems(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template('categoryview.html', category=category, items=items)


@app.route('/catalog/<int:category_id>/items/new')
def newItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        newItem = Item(name=reqeust.form['name'], description=request.form[
                       'description'], price=request.form['price'], category_id=category_id, user_id=category.user_id)
        session.add(newItem)
        session.commit()
        flash('New Item, %s, successfully created.' % (newItem.name))
        return redirect(url_for('showCategoryItems, category_id=category_id'))
    else:
        return render_template('newitem.html', category_id=category_id)


# REVIEW: UPDATE WITH TESTER CODE FOR ITEM
@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem():
    if request.method == 'GET':
        return render_template('testedit.html', categories=categories, item=item)
    else:
        session.commit(item)
        flash("The item '%s' has been removed." % item.name, "success")
        return redirect(url_for('home'))


@app.route('/item/<int:item>/delete', methods=['GET', 'POST'])
def deleteItem():
    """Find and delete an item"""
    categories = session.query(Category).all()
    item = session.query(Item).get(item_id)
    if request.method == 'GET':
        return render_template('rawdelete.html', categories=categories, item=item)
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
