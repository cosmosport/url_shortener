import string, basen, sqlite3, configparser
from flask import g


config = configparser.ConfigParser()
config.read("settings.ini")


DATABASE = "url_shortener.sqlite"
ALPHABET = string.ascii_letters + string.digits


def db():
    if not hasattr(g, "db"):
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def str_with_prefix_from_num(id: int) -> str:
    return config["URL"]["APP_BASE"] + basen.int2base(id, ALPHABET)


def str_from_num(id: int) -> str:
    return basen.int2base(id, ALPHABET)


def num_from_str(link: str) -> int:
    # str_from_num(9223372036854775807) == k9viXaIfiWh (11 characters)
    if len(link) <= 11:
        n = basen.base2int(link, ALPHABET)
        # 9223372036854775807 is the max value of int for sqlite3 (2^63-1)
        if n <= 9223372036854775807:
            return n
        return 0
    return 0


def id_from_short_link(link: str) -> int:
    """
    If the link is not found in the database, -- returns "0"
    """
    # Search id if the link was generated automatically
    link_id = num_from_str(link)
    try:
        db_row = db().execute("SELECT id FROM links WHERE id=?", (link_id,)).fetchone()
    except OverflowError:
        db_row = None
    if db_row:
        return db_row["id"]
    # Search id if short link was entered by user
    db_row = (
        db()
        .execute("SELECT link_id FROM short_links WHERE short_link=?", (link,))
        .fetchone()
    )
    if db_row:
        custom_shotr_link_id = db_row["link_id"]
        return custom_shotr_link_id
    return 0


def short_link_from_id(id: int) -> str:
    """
    If id is not found in the database, -- returns an empty string
    """
    db_row = (
        db()
        .execute("SELECT short_link FROM short_links WHERE link_id=?", (id,))
        .fetchone()
    )
    if db_row:
        return db_row[0]
    else:
        out_id = str_from_num(id)
        # check if the id stored in the database
        db_row = db().execute("SELECT id FROM links WHERE id=?", (id,)).fetchone()
        if db_row:
            return out_id
        return ""


def id_from_source_link(source_link: str) -> int:
    """
    If the link is not found in database, -- returns 0
    """
    db_row = (
        db().execute("SELECT id FROM links WHERE link=?", (source_link,)).fetchone()
    )
    if db_row:
        return int(db_row["id"])
    return 0


def custom_short_link(link_id) -> str:
    db_row = (
        db()
        .execute("SELECT short_link FROM short_links WHERE link_id=?", (link_id,))
        .fetchone()
    )
    if db_row:
        return db_row["short_link"]
    return ""


def update_custom_short_link(link_id, value: str):
    db().execute(
        "UPDATE short_links SET short_link=? WHERE link_id=?", (value, link_id)
    )
    db().commit()


def insert_custom_short_link(link_id, value: str):
    db().execute(
        "INSERT INTO short_links (short_link, link_id) VALUES (?, ?)",
        (value, str(link_id)),
    )
    db().commit()


def source_link(link_id):
    db_row = (
        db()
        .execute("SELECT link as source_link FROM links WHERE links.id=?", (link_id,))
        .fetchone()
    )
    if db_row:
        return db_row["source_link"]
    return ""


def update_source_link(link_id, value: str):
    db().execute("UPDATE links SET link=? WHERE id=?", (value, link_id))
    db().commit()


def delete_custom_short_link(link_id):
    db().execute("DELETE FROM short_links WHERE link_id=?", (link_id,))
    db().commit()


def user_id_from_name(user_name: str) -> int:
    db_row = db().execute("SELECT id FROM users WHERE name=?", (user_name,)).fetchone()
    if db_row:
        return int(db_row["id"])
    return 0


def insert_source_link(user_id, value: str):
    db().execute(
        "INSERT INTO links (user_id, link, redirect_cnt) VALUES (?, ?, 0)",
        (str(user_id), value),
    )
    db().commit()


def save_custom_short_link(link_id, value: str):
    if custom_short_link(link_id):
        update_custom_short_link(link_id, value)
    else:
        insert_custom_short_link(link_id, value)


def insert_user(user_name, password):
    db().execute(
        "INSERT INTO users (name, password) VALUES (?, ?)", (user_name, password)
    )
    db().commit()


def update_redirections_counter(count=0, link_id=0):
    db().execute(
        "UPDATE links SET redirect_cnt=? WHERE id=?", (str(count), str(link_id))
    )
    db().commit()


def get_table_of_links(user_name: str):
    db_rows = (
        db()
        .execute(
            "SELECT link, links.id, redirect_cnt, row_number() over (order by links.id desc) as num "
            "FROM links, users WHERE links.user_id=users.id and users.name=?",
            (g.logged_username,),
        )
        .fetchall()
    )
    for db_row in db_rows:
        yield dict(
            num=db_row["num"],
            source_link=db_row["link"],
            short_link=config["URL"]["APP_BASE"] + short_link_from_id(db_row["id"]),
            redirect_cnt=db_row["redirect_cnt"],
            link_id=db_row["id"],
        )


def main():
    print(str_from_num(9223372036854775807))
    return


if __name__ == "__main__":
    main()
