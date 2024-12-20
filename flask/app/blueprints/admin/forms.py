from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, InputRequired

class ModifyTransactionForm(FlaskForm):
    original_points = IntegerField(
        'Original Points',
        validators=[InputRequired(), NumberRange(min=0, message="Points must be positive.")]
    )
    description = StringField(
        'Description',
        validators=[DataRequired(), Length(max=100)]
    )
    submit = SubmitField('Update Transaction')

class MarkGiftCardSentForm(FlaskForm):
    submit = SubmitField('Mark as Sent')


class DeleteTransactionForm(FlaskForm):
    submit = SubmitField('Delete')

