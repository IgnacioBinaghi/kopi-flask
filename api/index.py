from flask import Flask, render_template, url_for, flash, redirect, request
from util.get_quote import get_quote
from util.get_new_workspaces import get_cafes
from util.get_coord import get_location

app = Flask('__name__')

@app.route("/", methods=["GET", "POST"])
def home():
    URL = "http://maps.googleapis.com/maps/api/geocode/json"
    if request.method == 'POST':
        preferences = request.form.getlist('preferences')
        location = request.form.get("location")
        location = get_location(location)
        cafes = get_cafes(location)
        print(cafes)
        return render_template('home.html', username='ignacio', cafes = cafes)
    return render_template('home_initial.html', username='ignacio')


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
    app.run(debug=True)
