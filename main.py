from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']
APPLICATION_NAME = "Catalog"

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind=engine

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
    categories = session.query(Category).all()
    items=session.query(Item).order_by(desc(Item.created)).limit(10).all()
    return render_template('main.html', categories=categories, items=items)

@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm(request.form)
#     if request.method == 'POST' and form.validate():
#         user = User(form.username.data)
#         session.add(user)
#         flash('Thanks for registering')
#         return redirect("google.com", code=302)
#     return render_template('register.html', form=form)
@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
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
		response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type']='application/json'
		return response

	access_token = credentials.access_token
	url=('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	if result.get('error') is not None:
	    response = make_response(json.dumps(result.get('error')), 500)
	    response.headers['Content-Type'] = 'application/json'
	    return response

	gplus_id = credentials.id_token['sub']

	if result['user_id']!=gplus_id:
		response=make_response(json.dumps("Token's user ID doesn't match given user ID."),401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is valid for this app.
	if result['issued_to']!=CLIENT_ID:
		response = make_response(json.dumps("Token's client ID does not match app's."),401)
		print "Token's client ID does not match app's."
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id==stored_gplus_id:
		response=make_response(json.dumps('Current user is already connected.'),200)
		response.headers['Content-Type'] = 'application/json'
		return response

    # Store the access token in the session for later use.
	login_session['credentials'] = credentials
	login_session['gplus_id'] = gplus_id

	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token':credentials.access_token, 'alt':'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

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


# @app.route('/catalog/categories')
# def categoryList():
#     output = ''
#     l = Category.query.all()
#     for i in l:
#         output += str(i.name)
#         output += "</br>"
#     return output

@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'),401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        #Reset session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/catalog/categories/new', methods=['GET','POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name = request.form['name'])
        session.add(newCategory)
        flash('New category successfully created')
        session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('newCategory.html')

@app.route('/catalog/category/<string:category_name>/edit')
def editCategory(category_id):
    return "Edit category"

@app.route('/catalog/category/<int:category_id>/delete')
def deleteCategory():
    return "Delete category"

@app.route('/catalog/<string:category_name>/items')
@app.route('/catalog/<string:category_name>')
def categoryItems(category_name):
    output = ''
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category = category).all()
    return render_template('categoryview.html', category = category, items=items)

@app.route('/catalog/<int:category_id>/items/new')
def newItem():
    output = ''
    l = session.query(Item).all()
    for i in l:
        output += str(i.name)
        output += "</br>"
    return output
@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit')
def editItem():
    return "Edit item"

@app.route('/catalog/<int:category_id>/item/<int:item_id>/delete')
def deleteItem():
    return "Delete item"



if __name__ == '__main__':
	app.secret_key = 'wtha3U192fJdNodDBl4CtGsG'
app.debug = True
app.run(host = '0.0.0.0', port = 8080)