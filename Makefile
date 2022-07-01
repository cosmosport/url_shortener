venv/bin/activate:
	python3 -m venv venv
	. venv/bin/activate; pip install -r requirements.txt;

setup: venv/bin/activate
	. venv/bin/activate; pip install -r dev.txt

lint: venv/bin/activate
	. venv/bin/activate; black .

init:
	cd url_shortener && sqlite3 url_shortener.sqlite < init.sql

dev:
	cd url_shortener && FLASK_APP=app FLASK_ENV=development python -m flask run 

run:
	cd url_shortener && FLASK_APP=app FLASK_ENV=production python -m flask run 