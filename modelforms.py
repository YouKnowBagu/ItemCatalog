from wtforms import Form, BooleanField, StringField, validators, TextField
from wtforms.widgets import TextArea
from wtforms_alchemy import ModelForm
from database_setup import Category, Item
from flask_wtf import Form

class CategoryForm(ModelForm, Form):
    class Meta:
        model = Category
        include = ['user_id']

class ItemForm(ModelForm, Form):
    class Meta:
        model = Item
        include = ['user_id']