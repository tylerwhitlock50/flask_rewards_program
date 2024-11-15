from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileRequired, FileAllowed

class EarnPointsForm(FlaskForm):
    code = StringField(
        'Enter Code', 
        validators=[
            DataRequired(message="Code is required."),
            Length(max=20, message="Code must be 20 characters or fewer.")
        ]
    )
    receipt = FileField(
        'Upload Receipt',
        validators=[
            FileRequired(message="A receipt file is required."),
            FileAllowed(['jpg', 'png', 'pdf'], "Only JPG, PNG, and PDF files are allowed.")
        ]
    )
    submit = SubmitField('Submit')
