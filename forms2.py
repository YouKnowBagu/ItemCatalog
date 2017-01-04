from wtforms import Form, BooleanField, StringField, validators, TextField
from wtforms.widgets import TextArea


class addEdit(Form):
    name = StringField('Name',[validators.Length(min=3, max=20)])
    description = TextField('Description',[validators.Length(min=3, max=20)], widget=TextArea())