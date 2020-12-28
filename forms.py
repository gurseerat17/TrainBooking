from flask_wtf import FlaskForm
from wtforms import SubmitField,IntegerField,DateField
from wtforms.validators import DataRequired

class AdminAddTrains(FlaskForm):
    train_no= IntegerField('TrainNo.', validators=[DataRequired()])
    date=DateField('Date',validators=[DataRequired()],format=f'%d-%m-%Y')
    ac_coaches=IntegerField('No. Of AC Coaches',validators=[DataRequired()])
    slp_coaches=IntegerField('No. Of Sleeper Coaches',validators=[DataRequired()])
    security_key=IntegerField('Security Key',validators=[DataRequired()])
    submit=SubmitField('Add')