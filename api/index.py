from flask import Flask, render_template, url_for, flash, redirect, request
from util.get_quote import get_quote
import json
import csv
from util.get_new_workspaces import get_cafes


app = Flask(__name__, template_folder='templates')


@app.route("/home")
def home():
    cafes = get_cafes()
    return render_template("index.html", username = 'ignacio', cafes=cafes)


@app.route("/login", methods=["GET", "POST"])
def login():
    quote = get_quote()
    if request.method == "POST":
        name = request.form.get("name").lower()
        email = request.form.get("email").lower()
        password = request.form.get("password")

    return render_template("login.html", quote=quote)


@app.route("/register", methods=["GET", "POST"])
def register():
    quote = get_quote()
    validity = ''
    if request.method == "POST":
        name = request.form.get("name").lower()
        email = request.form.get("email").lower()
        password = request.form.get("password")
    return render_template("create_account.html", quote=quote)


if __name__ == '__main__':
    app.run()
