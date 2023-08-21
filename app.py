from flask import Flask, render_template, url_for, flash, redirect, request, session, flash
from flask import render_template, url_for, flash, redirect, request, session, flash
import flask_login
from get_new_workspaces import get_cafes
from get_coord import get_location
import pickle
from kopi_server import *
from pwd_hash import *


uri = "mongodb+srv://binaghiignacio:Pepapepa001025762@kopiserver.puw29km.mongodb.net/?retryWrites=true&w=majority"
user_data_manager = UserDataManager(uri)
users = user_data_manager.get_users()

app = Flask('__name__', template_folder='templates')
app.secret_key = 'NACHOTON'


login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(username):
    user_data = user_data_manager.get_user(username)
    if user_data:
        user = User()
        user.id = username
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
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user_data = {
            "username": username,
            "email": email,
            "password": hash(password),
            "bio": "",
            "workspaces": [],
            "friends": {'connected': [], 'sent': [], 'received': []}
        }

        # Attempt to create the user in the database
        if user_data_manager.create_user(user_data):
            user = User()
            user.id = username
            flask_login.login_user(user)
            return redirect(url_for('home'))
        else:
            msg = 'An Account With That Username or Email Already Exists'
        
    return render_template('register.html', msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method != 'POST':
        return render_template('login.html', msg=msg)
    
    username = request.form.get('username')
    password = request.form.get('password')

    # Fetch user data from MongoDB
    user_data = user_data_manager.get_user(username)

    if user_data and check_password(password, user_data.get('password')):
        user = User()
        user.id = username
        flask_login.login_user(user)
        return redirect(url_for('home'))
    
    msg = 'Username or Password Incorrect'
    return render_template('login.html', msg=msg)



@app.route("/", methods=["GET", "POST"])
@flask_login.login_required
def home():
    user_data = user_data_manager.get_user(flask_login.current_user.id)
    
    workspaces = user_data.get('workspaces')
    friends = user_data.get('friends').get('connected')
    
    return render_template('index.html', username=flask_login.current_user.id, workspaces=workspaces, friends=friends)



@app.route("/search", methods=["GET", "POST"]) # Search new cafes
@flask_login.login_required
def search():
    URL = "http://maps.googleapis.com/maps/api/geocode/json"
    if request.method == 'POST':
        preferences = request.form.getlist('preferences')
        location = request.form.get("location")
        cafe_location = get_location(location)
        cafes = get_cafes(cafe_location)
        return render_template('discover.html', username=flask_login.current_user.id, cafes=cafes)
    return render_template('discover_initial.html', username=flask_login.current_user.id)


@app.route("/friends", methods=["GET", "POST"]) # Friends page
@flask_login.login_required
def friends():
    user_data = user_data_manager.get_user(flask_login.current_user.id)
    connected_friends = user_data.get('friends').get('connected')
    requests_received = user_data.get('friends').get('received')
    requests_sent = user_data.get('friends').get('sent')
    
    all_users = user_data_manager.get_usernames()  # Assuming all_users is a list of usernames
    
    filtered_users = [
        username for username in all_users
        if username != flask_login.current_user.id
        and username not in connected_friends
        and username not in requests_received
        and username not in requests_sent
    ]
    
    return render_template('friends.html', username=flask_login.current_user.id, friends=connected_friends, users=filtered_users, requests_received=requests_received)



@app.route("/send_request", methods=["POST"]) # Add friend
@flask_login.login_required
def send_request():
    friend = request.form['name']

    user_data_manager.add_sent_request(flask_login.current_user.id, friend)
    
    user_data_manager.add_received_request(friend, flask_login.current_user.id)
    
    return f'request sent to {friend}'


@app.route("/accept_request", methods=["POST"]) # Add friend
@flask_login.login_required
def accept_request():
    friend = request.form['name']
    
    current_user_id = flask_login.current_user.id

    user_data_manager.remove_received_request(current_user_id, friend)
    user_data_manager.remove_sent_request(friend, current_user_id)

    
    user_data_manager.add_connected_friend(current_user_id, friend)
    user_data_manager.add_connected_friend(friend, current_user_id)
    
    return f'{friend} added as a friend'

@app.route("/remove_friend", methods=["POST"]) # Add friend
@flask_login.login_required
def remove_friend():
    friend = request.form['name']
    
    current_user_id = flask_login.current_user.id
    
    user_data_manager.remove_connected_friend(current_user_id, friend)
    user_data_manager.remove_connected_friend(friend, current_user_id)
    
    return f'{friend} removed'


@app.route('/<username>')
@flask_login.login_required
def profile(username):
    if username == flask_login.current_user.id:
        return redirect(url_for('my_profile'))
    user_data = user_data_manager.get_user(username)
    try:
        bio = user_data.get('bio')
        bio = 'No bio yet'
    except:
        pass
    if user_data:
        return render_template('profile.html', username=username, bio=bio, workspaces=user_data.get('workspaces'))
    else:
        return redirect(url_for('home'))
    

@app.route("/my_profile", methods=["GET", "POST"])
@flask_login.login_required
def my_profile():
    if request.method == 'POST':
        bio = request.form.get('bio')
        user_data_manager.update_bio(flask_login.current_user.id, bio)
        return redirect(url_for('my_profile'))
    
    user_data = user_data_manager.get_user(flask_login.current_user.id)
    workspaces = user_data.get('workspaces')
    bio = user_data.get('bio')
    if bio == '':
        return render_template('my_profile.html', username=flask_login.current_user.id, bio='You have not added a bio yet', workspaces=workspaces)
    else:
        return render_template('my_profile.html', username=flask_login.current_user.id, bio=bio, workspaces=workspaces)


@app.route('/add_workspace', methods=['POST'])
@flask_login.login_required
def add_workspace():
    data = request.get_json()
    pic = data['pic']
    yelp = data['yelp']
    cafe_name = data['cafe_name']
    address = data['address']
    attending = data['attending']

    current_user_id = flask_login.current_user.id

    user_data_manager.get_users()

    workspace = [cafe_name, address, pic, yelp, attending]

    user_data_manager.add_workspace(current_user_id, workspace)

    return f'Workspace Added'


@app.route('/remove_workspace', methods=['POST'])
@flask_login.login_required
def remove_workspace():
    data = request.get_json()
    pic = data['pic']
    yelp = data['yelp']
    cafe_name = data['cafe_name']
    address = data['address']
    attending = data['attending']
    
    current_user_id = flask_login.current_user.id
    user_data = user_data_manager.get_user(current_user_id)

    workspace = [cafe_name, address, pic, yelp, attending]
    
    user_data_manager.remove_workspace(current_user_id, workspace)
    
    return f'Workspace Removed'



@app.route('/log_out')
def logout():
    flask_login.logout_user()
    return render_template('login.html')


@app.route('/delete_acc')
@flask_login.login_required
def delete_acc():
    user = flask_login.current_user.id
    user_data_manager.remove_user(user)
    flask_login.logout_user()
    return render_template('register.html')


@app.route("/developer", methods=["GET", "POST"]) # Developer Portal
@flask_login.login_required
def developer():
    if flask_login.current_user.id != 'ignacio':
        return redirect(url_for('home'))
    users = user_data_manager.get_usernames()
    users = list(users)
    return render_template('developer.html', users=users)

@app.route('/remove_account', methods=['POST']) # Remove acc for developer portal
def remove_account():
    user = request.form['name']
    user_data_manager.remove_user(user)
    return 'account removed'

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False)
