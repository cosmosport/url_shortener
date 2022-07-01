from flask_wtf import FlaskForm
from wtforms import StringField, validators, PasswordField, TextAreaField


class LoginForm(FlaskForm):
    name = StringField('name', validators=[validators.DataRequired()])
    password = PasswordField("password", validators=[validators.DataRequired()])


class RegisterForm(FlaskForm):
    name = StringField('name', validators=[validators.DataRequired()])
    password = PasswordField("password", validators=[validators.DataRequired()])
    password_rep = PasswordField("password", validators=[validators.DataRequired()])


class UrlEditForm(FlaskForm):
    source_link = TextAreaField("source_link",
                         validators=[validators.DataRequired()],
                         render_kw={"class": "form-control", "rows": "10"}
    )
    short_link = StringField("short_link",
                        validators=[validators.DataRequired()],
                        render_kw={"class": "form-control"}
    )