from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind=engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

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

@app.route('/')
@app.route('/catalog/')
def home():
    return "Home"

@app.route('/catalog/categories')
def categoryList():
    output = ''
    l = session.query(Category).all()
    for i in l:
        output += str(i.id)
        output += "</br>"
    return output

@app.route('/catalog/categories/new')
def newCategory():
    return "New category"

@app.route('/catalog/category/<int:category_id>/edit')
def editCategory(category_id):
    return "Edit category"

@app.route('/catalog/category/<int:category_id>/delete')
def deleteCategory():
    return "Delete category"

@app.route('/catalog/<int:category_id>/items')
@app.route('/catalog/<int:category_id>')
def categoryItems():
    return "Category items"

@app.route('/catalog/<int:category_id>/items/new')
def newItem():
    return "New item"

@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit')
def editItem():
    return "Edit item"

@app.route('/catalog/<int:category_id>/item/<int:item_id>/delete')
def deleteItem():
    return "Delete item"



if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)