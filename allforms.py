from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField,IntegerField,FieldList,Form,FormField
from wtforms.validators import DataRequired, Length,  EqualTo
from wtforms.fields.html5 import DateField

class RegistrationForm(FlaskForm):
    agent_name = StringField('Enter Your Name',
                           validators=[DataRequired(), Length(min=2, max=30)])
    credit_card = StringField('Credit Card Number',
                        validators=[DataRequired()])
    address = StringField('Address',
                        validators=[DataRequired()])
    password = PasswordField('Set a Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    agent_id = StringField('Agent ID',
                        validators=[DataRequired()])
    agent_name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=30)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    

class AdminAddTrains(FlaskForm):
    train_no= IntegerField('TrainNo.', validators=[DataRequired()])
    date=DateField('DatePicker', format='%Y-%m-%d',validators=[DataRequired()])
    ac_coaches=IntegerField('No. Of AC Coaches')
    slp_coaches=IntegerField('No. Of Sleeper Coaches')
    security_key=PasswordField('Security Key',validators=[DataRequired()])
    submit=SubmitField('Add')

class Passenger(Form):
    namep=StringField('Name')
    age=IntegerField('Age')
    gender=StringField('Gender')


class Passengers(FlaskForm):
    train_no= IntegerField('TrainNo.')
    date=DateField('DatePicker', format='%Y-%m-%d',validators=[DataRequired()])
    coach_type=SelectField('Coach Type',choices=['Select Coach Type','AC','Sleeper'])
    passengers_no=IntegerField('Number of Passengers')
    passengers=FieldList(FormField(Passenger))
   
    submit=SubmitField('Add')

  


class BookTrains(FlaskForm):
    train_no= IntegerField('TrainNo.', validators=[DataRequired()])
    date=DateField('DatePicker', format='%Y-%m-%d',validators=[DataRequired()])
    coach_type=SelectField('Coach Type',choices=['Select Coach Type','AC','Sleeper'],validators=[DataRequired()])
    passengers_no=IntegerField('Number of Passengers',validators=[DataRequired()])
    passengers=FieldList(FormField(Passenger),min_entries=1,max_entries=30)
    # print(passengers)
    submit=SubmitField('Add')
