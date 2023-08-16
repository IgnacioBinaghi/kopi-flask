from flask import Flask, render_template, url_for, flash, redirect, request, session, flash
from flask import render_template, url_for, flash, redirect, request, session, flash
import flask_login
from get_new_workspaces import get_cafes
from get_coord import get_location
from kopi_db import *
import pickle

app = Flask('__name__', template_folder='templates')
app.secret_key = 'NACHOTON'


login_manager = flask_login.LoginManager()
login_manager.init_app(app)

users = load_dict('users.txt')

class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        global users
        users = load_dict('users.txt')
        if username in users:
            return render_template('register.html', msg = 'An Account With That Username Already Exists')
        else:
            users[username] = {'email': email, 'password': password, 'workspaces' : [], 'friends':[]}
            
            save_dict(users, 'users.txt')
    
            users = load_dict('users.txt')
            
            return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method != 'POST':
        return render_template('login.html')
    username = request.form.get('username')
    if username in users and request.form.get('password') == users[username]['password']:
        user = User()
        user.id = username
        flask_login.login_user(user)
        return redirect(url_for('home'))

    return render_template('login.html', msg = 'Username or Password Incorrect')


@app.route("/", methods=["GET", "POST"])
@flask_login.login_required
def home():
    users = load_dict('users.txt')
    session['users'] = users
    workspaces = users[flask_login.current_user.id]['workspaces']
    friends = users[flask_login.current_user.id]['friends']
    return render_template('index.html', username=flask_login.current_user.id, workspaces = workspaces, friends=friends)

@app.route("/search", methods=["GET", "POST"])
@flask_login.login_required
def search():
    URL = "http://maps.googleapis.com/maps/api/geocode/json"
    if request.method == 'POST':
        preferences = request.form.getlist('preferences')
        location = request.form.get("location")
        location = get_location(location)
        cafes = get_cafes(location)
        session['cafes'] = cafes
        return render_template('discover.html', username=flask_login.current_user.id, cafes = session.get('cafes'))
    return render_template('discover_initial.html', username=flask_login.current_user.id)


@app.route('/add', methods=['GET', 'POST'])
def add():
    data = request.get_json()
    pic = data['pic']
    yelp = data['yelp']
    cafe_name = data['cafe_name']
    address = data['address']
    attending = data['attending']

    users = load_dict('users.txt')

    workspaces = users[flask_login.current_user.id]['workspaces']

    workspaces.append([cafe_name, address, pic, yelp, attending])

    users[flask_login.current_user.id] = {'email': users[flask_login.current_user.id]['email'], 'password': users[flask_login.current_user.id]['password'], 'workspaces': workspaces, 'friends': users[flask_login.current_user.id]['friends']}
            
    save_dict(users, 'users.txt')
    
    users = load_dict('users.txt')
    
    return f'Workspace Added'

@app.route('/log_out')
def logout():
    flask_login.logout_user()
    return render_template('login.html')

@app.route('/delete_acc')
@flask_login.login_required
def delete_acc():
    remove_user(flask_login.current_user.id, 'users.txt')
    return render_template('register.html')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False)
