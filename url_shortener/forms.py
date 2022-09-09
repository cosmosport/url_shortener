from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    validators,
    PasswordField,
    TextAreaField,
    ValidationError,
)
from wtforms.validators import Length, EqualTo
from app_routines import config


class LoginForm(FlaskForm):
    name = StringField(
        "Имя: ",
        validators=[validators.DataRequired(message="Введите логин")],
        render_kw={"class": "form-control"},
    )

    password = PasswordField(
        "Пароль: ",
        validators=[validators.DataRequired(message="Введите пароль")],
        render_kw={"class": "form-control"},
    )


class RegistrationForm(FlaskForm):
    name = StringField(
        "Имя: ",
        validators=[validators.DataRequired(message="Введите логин")],
        render_kw={"class": "form-control"},
    )

    password = PasswordField(
        "Пароль: ",
        validators=[
            validators.DataRequired(message="Введите пароль"),
            Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов"),
        ],
        render_kw={"class": "form-control"},
    )

    password_rep = PasswordField(
        "Повторите пароль: ",
        validators=[
            validators.DataRequired(message="Введите пароль"),
            EqualTo("password", message="Пароли не совпадают"),
        ],
        render_kw={"class": "form-control"},
    )


class UrlEditForm(FlaskForm):
    def validate_ascii_alphanum_or_empty(form, field):
        if not ((field.data.isascii() and field.data.isalnum()) or not field.data):
            raise ValidationError(
                "Допустимы только латинские буквы и цифры или пустая строка"
            )

    source_link = TextAreaField(
        "Исходный URL: ",
        validators=[
            validators.DataRequired(),
            validators.URL(require_tld=True, message="Недопустимый URL"),
        ],
        render_kw={"class": "form-control", "rows": "10"},
    )

    app_base = config["URL"]["APP_BASE"]
    short_link = StringField(
        f'Короткая ссылка без префикса "{app_base}". Разрешены латинские буквы и цифры. Для автоматической генерации ссылки оставьте поле пустым:',
        validators=[
            validate_ascii_alphanum_or_empty,
        ],
        render_kw={"class": "form-control"},
    )
