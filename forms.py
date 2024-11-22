from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, EmailField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo

# create LoginForm model
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=24)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Submit")

class CreatePostForm(FlaskForm):
    title = StringField("Title:", validators=[DataRequired()])
    content = TextAreaField("Content:", validators=[DataRequired()])
    submit = SubmitField("Submit")




