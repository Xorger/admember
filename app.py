import os
from flask import Flask, render_template
import sqlite3

database_filename = "database.db"

sql_statements = [
    """CREATE TABLE IF NOT EXISTS users (
            user_id integer AUTOINCREMENT PRIMARY KEY,
            username text NOT NULL
            name text NOT NULL
            password_hash text NOT NULL
            status integer NOT NULL DEFAULT FALSE
            admin integer NOT NULL DEFAULT FALSE
            );"""
]

with sqlite3.connect(database_filename) as db:
    cursor = db.cursor
    for statement in sql_statements:
        cursor.execute(statement)

@app.route("/")
def index():
    return render_template("index.html")
