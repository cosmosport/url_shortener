CREATE TABLE users (
    id integer primary key autoincrement,
    name TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL 
);

CREATE TABLE links (
    id integer primary key autoincrement,
    user_id INTEGER,
    link TEXT NOT NULL,
    FOREIGN KEY (user_id) 
        REFERENCES users (user_id) 
            ON DELETE CASCADE 
            ON UPDATE NO ACTION
);
