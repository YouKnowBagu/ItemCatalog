from wtforms import Form
from wtforms_alchemy import ModelForm
from models import Category, Item
from flask_wtf import Form

class CategoryForm(ModelForm, Form):
    class Meta:
        model = Category
        include = ['user_id']

class ItemForm(ModelForm, Form):
    class Meta:
        model = Item
        include = ['user_id']