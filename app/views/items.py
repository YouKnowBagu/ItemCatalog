"""Module for all item related views"""

from flask import session as login_session
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import login_required

from app.database import session
from app.modelforms import ItemForm
from app.models import Category, Item

itemModule = Blueprint('items', __name__)


@itemModule.route('/<int:category_id>/<int:item_id>/JSON')
def ItemJSON(category_id, item_id):
    """JSON endpoint for individual items."""
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


@itemModule.route('/<int:category_id>/<int:item_id>', methods=['GET'])
def viewItem(category_id, item_id):
    """View and controls for individual item."""
    category = session.query(Category).filter_by(id=category_id).first()
    item = session.query(Item).filter_by(
        id=item_id, category_id=category.id).first()
    if request.method == 'GET':
        return render_template('items/item.html', category=category, item=item)


@itemModule.route('/<int:category_id>/item/new', methods=['GET', 'POST'])
@login_required
def newItem(category_id):
    """View containing the form for adding an item to a category."""
    category = session.query(Category).filter_by(id=category_id).first()
    categories = session.query(Category).all()
    form = ItemForm(request.form)
    if request.method == 'POST' and form.validate():
        newitem = Item(
            name=request.form['name'],
            description=request.form['description'],
            user_id=login_session['user_id'],
            category_id=category_id)
        session.add(newitem)
        session.commit()
        flash('New Item, %s, successfully created.' % (newitem.name))
        return redirect(url_for('site.home'))
    else:
        return render_template(
            'items/newitem.html',
            category=category,
            categories=categories,
            form=form)


@itemModule.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def editItem(item_id):
    """View for the form to edit an item."""
    editeditem = session.query(Item).filter_by(id=item_id).first()
    form = ItemForm(request.form)
    if request.method == 'GET':
        return render_template(
            'items/editItem.html', item=editeditem, form=form)
    if request.method == 'POST' and form.validate():
        editeditem.name = request.form['name']
        editeditem.description = request.form['description']
        session.commit()
        flash('Item Successfully Edited %s' % editeditem.name)
        return redirect(url_for('site.home'))


@itemModule.route('/item/<int:item_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(item_id):
    """Find and delete an item."""
    item = session.query(Item).filter_by(id=item_id).one()
    form = ItemForm(request.form)
    if request.method == 'GET':
        return render_template('items/deleteItem.html', item=item, form=form)
    else:
        session.delete(item)
        session.commit()
        flash("The item '%s' has been removed." % item.name, "success")
        return redirect(url_for('site.home'))
