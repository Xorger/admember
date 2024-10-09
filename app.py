import os
from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

database_filename = "database.db"

sql_statements = [
    """CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    status BOOLEAN NOT NULL DEFAULT FALSE,
    admin BOOLEAN NOT NULL DEFAULT FALSE
    );"""
]

with sqlite3.connect(database_filename) as db:
    cursor = db.cursor()
    for statement in sql_statements:
        cursor.execute(statement)
    db.commit()

@app.route("/")
def index():
    with sqlite3.connect(database_filename) as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users")
    return render_template("index.html", rows=cursor.fetchall())
