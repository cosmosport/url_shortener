import bcrypt
from flask import (
    Flask,
    render_template,
    g,
    session,
    redirect,
    flash,
    url_for,
)
from forms import LoginForm, UrlEditForm, RegistrationForm
from app_routines import (
    config,
    db,
    id_from_short_link,
    short_link_from_id,
    str_from_num,
    id_from_source_link,
    insert_custom_short_link,
    source_link,
    update_source_link,
    delete_custom_short_link,
    user_id_from_name,
    insert_source_link,
    save_custom_short_link,
    insert_user,
    update_redirections_counter,
    get_table_of_links
)

app = Flask(__name__)
app.config["X-KEY"] = config["Secret"]["X-KEY"]
app.secret_key = config["Secret"]["secret_key"]


@app.before_request
def global_vars():
    if session.get("logged_in_username"):
        g.logged_username = session["logged_in_username"]


@app.route("/<short_link>")
def redir(short_link):
    link_id = id_from_short_link(short_link)
    db_row = (
        db()
        .execute("SELECT link, redirect_cnt FROM links WHERE id=?", (link_id,))
        .fetchone()
    )
    if db_row:
        source_link = db_row["link"]
        redirect_cnt = db_row["redirect_cnt"]
        redirect_cnt += 1
        update_redirections_counter(count=redirect_cnt, link_id=link_id)
        return redirect(source_link)
    return "<h1>Error 404 - Page not found<br> Ошибка 404 - Страница не найдена</h1>"


@app.route("/")
def frontpage():
    if not session.get("logged_in_username"):
        return redirect(url_for("about"))
    return render_template(
        "links_table.html",
        rows = get_table_of_links(g.logged_username)
    )


@app.route("/s/about", endpoint="about")
@app.route("/s/about/")
def aboutpage():
    return render_template("about.html")


@app.route("/s/contacts", endpoint="contacts")
@app.route("/s/contacts/")
def contactpage():
    return render_template("contacts.html")


@app.route("/link_delete/<link_id>", methods=["GET", "POST"], endpoint="link_delete")
def link_delete(link_id):
    db().execute("DELETE FROM links WHERE id=?", (link_id,))
    db().commit()
    flash("Запись удалена.", "alert-success")
    return redirect("/")


@app.route("/linkedit/<link_id>", methods=["GET", "POST"], endpoint="linkedit")
def link_edit(link_id):
    source_link_ = source_link(link_id)
    form = UrlEditForm(
        source_link=source_link_, short_link=short_link_from_id(int(link_id))
    )
    if form.validate_on_submit():
        new_souce_link_saved = False
        if form.source_link.data != source_link_:
            update_source_link(link_id, form.source_link.data)
            new_souce_link_saved = True
        if not form.short_link.data:
            # user removes the short link - delete it from the table
            delete_custom_short_link(link_id)
            # if there is no short link in the short_links table -- it wiss be generated from the link_id automatecaly
            if new_souce_link_saved:
                flash("Исходная ссылка сохранена, короткая ссылка была сгенерирована автоматически.", "alert-success")
            else:
                flash("Короткая ссылка была сгенерирована автоматически.", "alert-success")
            return redirect("/")
        short_link_id = id_from_short_link(form.short_link.data)
        if short_link_id == int(link_id):
            # saving the short link in the database is not required
            if new_souce_link_saved:
                flash("Исходная ссылка сохранена.", "alert-success")
            return redirect("/")
        else:
            # User has edited the short link
            if short_link_id == 0:
                # edited short link does not exist yet & it will be saved
                save_custom_short_link(link_id, form.short_link.data)
                if new_souce_link_saved:
                    flash("Исходная и короткая ссылки сохранены.", "alert-success")
                else:
                    flash(f'Новое значение короткой ссылки "{form.short_link.data}" сохранено', "alert-success")
                return redirect("/")
            else:  # edited short link already exist
                form.short_link.errors.append(
                    f'Короткая ссылка "{form.short_link.data}" занята. Укажите другую короткую ссылку.'
                )
                form.short_link.data = str_from_num(int(link_id))
                if new_souce_link_saved:
                    flash("Исходная ссылка сохранена.", "alert-success")
    return render_template(
        "link_edit.html",
        form=form,
        header_title="Редактировать URL",
    )


@app.route("/s/linknew", methods=["GET", "POST"], endpoint="linknew")
def linknew():
    user_id = user_id_from_name(g.logged_username)
    form = UrlEditForm(source_link="", short_link="")
    if form.validate_on_submit():
        insert_source_link(user_id, form.source_link.data)
        if form.short_link.data:  # if user entered a short link
            if not id_from_short_link(form.short_link.data):
                # entered short link does not exist yet
                insert_custom_short_link(id_from_source_link(form.source_link.data), form.short_link.data)
                flash("Запись добавлена", "alert-success")
            else:
                form.short_link.errors.append(
                    f"Короткая ссылка '{form.short_link.data}' занята. Введите другую короткую ссылку."
                )
                return render_template(
                    "link_edit.html",
                    form=form,
                    header_title="Новая ссылка",
                )
        return redirect("/")
    return render_template(
        "link_edit.html",
        form=form,
        header_title="Новая ссылка",
    )


@app.route("/s/login", methods=["GET", "POST"], endpoint="login")
def loginpage():
    form = LoginForm()
    if form.validate_on_submit():
        db_row = (
            db()
            .execute(
                f"SELECT name, password FROM users WHERE name=?", (form.name.data,)
            )
            .fetchone()
        )
        password = form.password.data.encode("utf-8")
        if db_row and bcrypt.checkpw(password, db_row["password"]):
            # Password matched
            session["logged_in_username"] = form.name.data
            return redirect("/")
        else:
            flash("Неверные имя или пароль", "alert-danger")
    return render_template("login.html", form=form)


@app.route("/s/logout", endpoint="logout")
def logoutpage():
    session.pop("logged_in_username", None)
    return redirect("/")


@app.route("/s/registration", methods=["GET", "POST"], endpoint="registration")
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        if user_id_from_name(form.name.data):
            form.name.errors.append(
                f"Имя {form.name.data} уже зарегистрировано. Укажите другое имя."
            )
            return render_template("registration.html", form=form)
        if form.password.data != form.password_rep.data:
            flash("Пароли не совпадают.", "alert-warning")
            return render_template("registration.html", form=form)
        salt = bcrypt.gensalt()
        password = form.password.data.encode("utf-8")
        password_hash = bcrypt.hashpw(password, salt)
        insert_user(form.name.data, password_hash)
        flash(
            "Регистрация прошла успешно. Создайте Вашу первую ссылку:", "alert-success"
        )
        session["logged_in_username"] = form.name.data
        return redirect(url_for("linknew"))
    return render_template("registration.html", form=form)


if __name__ == "__main__":
    app.run()
