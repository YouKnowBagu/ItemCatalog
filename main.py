from flask import Flask, render_template, redirect, url_for, request
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, User, Category, Item
from forms import RegistrationForm

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind=engine

DBSession = scoped_session(sessionmaker(autocommit=False,
	autoflush=False,
	bind=engine))
session = DBSession()

Base.query = DBSession.query_property()

app = Flask(__name__)
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
    categories = Category.query.all()
    items=Item.query.order_by(desc(Item.created)).limit(10).all()
    return render_template('main.html', categories=categories, items=items)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data)
        session.add(user)
        flash('Thanks for registering')
        return redirect("google.com", code=302)
    return render_template('register.html', form=form)

# @app.route('/catalog/categories')
# def categoryList():
#     output = ''
#     l = Category.query.all()
#     for i in l:
#         output += str(i.name)
#         output += "</br>"
#     return output

@app.route('/catalog/categories/new')
def newCategory():
    return "New category"

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
    category = Category.query.filter_by(name=category_name).one()
    items = Item.query.filter_by(category = category).all()
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
    app.debug = True
    app.run(host = '0.0.0.0', port = 8080)