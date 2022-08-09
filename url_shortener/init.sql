CREATE TABLE users (
    id integer primary key autoincrement,
    name TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL 
);

CREATE TABLE links (
    id integer primary key autoincrement,
    user_id INTEGER,
    link TEXT NOT NULL,
    redirect_cnt INTEGER,
    FOREIGN KEY (user_id) 
        REFERENCES users (id) 
            ON DELETE CASCADE 
            ON UPDATE NO ACTION
);

CREATE TABLE short_links (
    id integer primary key autoincrement,
    link_id INTEGER UNIQUE,
    short_link TEXT NOT NULL UNIQUE,
    FOREIGN KEY (link_id)
        REFERENCES links (id)
            ON DELETE CASCADE 
            ON UPDATE NO ACTION
);
