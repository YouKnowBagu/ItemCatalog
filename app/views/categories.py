"""Module containing all category related views."""
from flask import session as login_session
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from app.database import session
from app.modelforms import CategoryForm
from app.models import Category, Item

categoryModule = Blueprint('categories', __name__)


@categoryModule.route('/category/new', methods=['GET', 'POST'])
@login_required
def newCategory():
    """Form view for creating a new category."""
    form = CategoryForm(request.form)
    if request.method == 'POST' and form.validate():
        createCategory = Category(
            name=request.form['name'],
            description=request.form['description'],
            user_id=login_session['user_id'])
        session.add(createCategory)
        flash('New category successfully created')
        session.commit()
        return redirect(url_for('site.home'))
    else:
        return render_template('categories/newCategory.html', form=form)


@categoryModule.route(
    '/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def editCategory(category_id):
    """Form view for editing category"""
    form = CategoryForm(request.form)
    editedcategory = session.query(Category).filter_by(id=category_id).first()
    owner = editedcategory.user_id
    if login_session['user_id'] == owner:
        if request.method == 'POST' and form.validate():
            if request.form['name'] and request.form['description']:
                editedcategory.name = request.form['name']
                editedcategory.description = request.form['description']
                flash('Category Successfully Edited %s' % editedcategory.name)
                return redirect(url_for('site.home'))
            else:
                return redirect(
                    url_for(
                        'categories.editCategory',
                        form=form,
                        category_id=category_id))
        else:
            return render_template(
                'categories/editCategory.html',
                category=editedcategory,
                form=form)
    else:
        return redirect(url_for('site.home'))


@categoryModule.route(
    '/category/<int:category_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    form = CategoryForm(request.form)
    owner = category.user_id
    if login_session['user_id'] == owner:
        if request.method == 'GET':
            return render_template(
                'categories/deleteCategory.html', category=category, form=form)
        items = session.query(Item).filter_by(category_id=category_id).all()
        if items:
            for i in items:
                session.delete(i)
        session.delete(category)
        session.commit()
        flash("The category '%s' has been removed." % category.name, "success")
        return redirect(url_for('site.home'))
    else:
        return redirect(url_for('site.home'))


@categoryModule.route('/<int:category_id>', methods=['GET'])
def viewCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).first()
    items = session.query(Item).filter_by(category_id=category.id).all()
    if request.method == 'GET':
        return render_template(
            'categories/category.html', category=category, items=items)


@categoryModule.route('/mycategories', methods=['GET'])
def userCategories():
    if not (current_user.is_active and current_user.is_authenticated):
        return redirect(url_for('auth.showLogin'))
    else:
        UserID = login_session['user_id']
        usercats = session.query(Category).filter_by(user_id=UserID).all()
        return render_template(
            'categories/userCategories.html', categories=usercats)


@categoryModule.route('/<int:category_id>/JSON')
def categoryItemsJSON(category_id):
    """JSON endpoint."""
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])
