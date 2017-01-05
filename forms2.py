from wtforms import Form, BooleanField, StringField, validators, TextField
from wtforms.widgets import TextArea
from wtforms_alchemy import ModelForm
from database_setup import Category

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        include = ['user_id']