from ast import dump
import sqlite3, bcrypt,string, basen, configparser
from textwrap import indent
from flask import Flask, render_template, current_app, g, request, session, redirect, g, flash, jsonify
from forms import LoginForm, UrlEditForm, RegisterForm


config = configparser.ConfigParser()
config.read("settings.ini")


app = Flask(__name__)
app.config['X-KEY'] = config["Secret"]["X-KEY"]
app.secret_key = config["Secret"]["secret_key"]


DATABASE = "url_shortener.sqlite"
ALPHABET = string.ascii_letters + string.digits
SHIRT_URL_PREFIX = config["URL"]["SHIRT_URL_PREFIX"]


def short_link_from_id(id:int)->str:
    return SHIRT_URL_PREFIX + basen.int2base(id, ALPHABET)


def logged_in_user_name()->str:
    if session.get("logged_in_username"):
        return session["logged_in_username"]
    else:
        return("")


@app.before_request
def global_vars():
    if session.get("logged_in_username"):
        g.logged = session["logged_in_username"]


def db():
    if not hasattr(g, 'db'):
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.route("/<short_link>")
def redir(short_link):
    link_id = basen.base2int(short_link, ALPHABET)
    source_link = db().execute(f"SELECT link FROM links WHERE id='{link_id}'").fetchone()[0]
    return redirect(source_link)


@app.route("/")
def frontpage():
    db_rows = db().execute(f"SELECT link, links.id, row_number() over (order by links.id desc) as num FROM links, users WHERE links.user_id=users.id and users.name='{logged_in_user_name()}'").fetchall()
    short_links = {}
    for db_row in db_rows:
        # Значение поля 'id' таблицы 'links' служит ключём для словаря 'short_links'.
        short_links[db_row['id']] = short_link_from_id(db_row['id'])
    return render_template("feed.html", rows=db_rows, short_links=short_links, logged_user_name=logged_in_user_name())


@app.route("/about")
@app.route("/about/")
def aboutpage():
    return render_template("about.html", logged_user_name=logged_in_user_name())


@app.route("/contact")
@app.route("/contact/")
def contactpage():
    return render_template("contacts.html", logged_user_name=logged_in_user_name())


@app.route("/linkedit/<link_id>", methods=["GET", "POST"], endpoint="linkedit")
def link_edit(link_id):
    db_row = db().execute(f"SELECT link as source_link FROM links WHERE links.id='{link_id}'").fetchone()
    form = UrlEditForm(source_link=db_row['source_link'], short_link=short_link_from_id(int(link_id)))
    if form.validate_on_submit():
        db().execute(
            "UPDATE links SET link=? WHERE id=?",
            (form.source_link.data, link_id)
        )
        db().commit()
        flash("Запись сохранена")
        return redirect("/")
    return render_template("link_edit.html", link_id=link_id, form=form, logged_user_name=logged_in_user_name(), header_title="Редактировать URL")


@app.route("/linknew", methods=["GET", "POST"], endpoint="linknew")
def linknew():
    form = UrlEditForm(source_link="", short_link="")
    if form.validate_on_submit():
        logged_user_name_id = db().execute(f"SELECT id FROM users WHERE name='{logged_in_user_name()}'").fetchone()
        db().execute(
            "INSERT INTO links (user_id, link) VALUES (?, ?)",
            (str(logged_user_name_id["id"]), form.body.data)
        )
        db().commit()
        flash("Запись добавлена")
        return redirect("/")
    return render_template("link_edit.html", form=form, logged_user_name=logged_in_user_name(), header_title="Новая ссылка")


@app.route("/login", methods=["GET", "POST"], endpoint="login")
def loginpage():
    form = LoginForm()
    if form.validate_on_submit():
        db_row = db().execute(f"SELECT name, password FROM users WHERE name='{form.name.data}'").fetchone()
        password = form.password.data.encode('utf-8')
        if db_row and bcrypt.checkpw(password, db_row['password']):
            # Пароль совпал
            session["logged_in_username"] = form.name.data
            flash("Вы успешно вошли на сайт")
            return redirect("/")
        else:
            flash("Неверные имя или пароль")
    return render_template("login.html", form=form, logged_user_name=logged_in_user_name())


@app.route("/logout", endpoint="logout")
def logoutpage():
    session.pop("logged_in_username", None)
    flash("Вы вышли. До новых встреч!")
    return redirect("/")


@app.route('/register', methods=["GET", "POST"], endpoint="register")
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name_cnt = db().execute(f"SELECT count(name) FROM users WHERE name='{form.name.data}'").fetchone()[0]
        if name_cnt > 0:
            flash(f"Имя {form.name.data} уже зарегистрировано. Укажите другое имя.")
            return render_template("register.html", form=form)
        if form.password.data != form.password_rep.data:
            flash("Пароли не совпадают.")
            return render_template("register.html", form=form)
        salt = bcrypt.gensalt() 
        password = form.password.data.encode('utf-8')
        password_hash = bcrypt.hashpw(password, salt)
        db().execute("INSERT INTO users (name, password) VALUES (?, ?)",
            (form.name.data, password_hash)
        )
        db().commit()
        flash("Регистрация прошла успешно")
        return redirect("/login")
    return render_template("register.html", form=form)


if __name__ == '__main__':
    app.run()
