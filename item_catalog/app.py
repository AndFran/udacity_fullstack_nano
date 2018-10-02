import random
import string
import json
import httplib2
import requests
import uuid
from flask import Flask, render_template, redirect, url_for, abort
from flask import request, make_response, flash, jsonify
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import User, Category, Item, Base
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from functools import wraps

CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']

engine = create_engine("sqlite:///cat2.db")
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = scoped_session(sessionmaker(bind=engine))  # does not work because of threading

app = Flask(__name__)


def generate_random_string():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))  # 32 char random sequence


def requires_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'email' not in login_session:
            return redirect('login')
        return func(*args, **kwargs)

    return wrapper


def generate_csrf_token():
    if '_csrf_token' not in login_session:
        login_session['_csrf_token'] = generate_random_string()
    return login_session['_csrf_token']


@app.before_request
def csrf_protect():
    """
    On every post request we check for the hidden embedded token
    """
    if request.method == "POST":
        token = login_session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)


app.jinja_env.globals['csrf_token'] = generate_csrf_token


@app.route('/login', methods=['GET', 'POST'])
def showLogin():
    state = generate_random_string()
    login_session['state'] = state

    if request.method == 'GET':
        return render_template('login.html', STATE=state)
    else:
        user_email = request.form.get('userEmail')
        password = request.form.get('userPassword')

        user = verify_user(user_email, password)
        if user is None:
            flash("User not found!")
            return render_template('login.html', STATE=state)
        login_session['email'] = user.email
        return redirect(url_for('index'))


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    if data.get('username') is None:
        login_session['username'] = data['email']

    current_user = session.query(User).filter_by(email=login_session['email']).first()
    if not current_user:
        # we create a new user if one does not exist
        create_user(login_session['username'])
    return "Redirecting...."


@app.route('/disconnect')
def disconnect():
    """
    Disconnects/logs out the user whether they have logged in with a password or OAUTH
    """
    access_token = login_session.get('access_token')
    if access_token:
        # try to revoke the token if any
        requests.post('https://accounts.google.com/o/oauth2/revoke',
                      params={'token': login_session['access_token']},
                      headers={'content-type': 'application/x-www-form-urlencoded'})

    if login_session.get('access_token'):
        del login_session['access_token']
    if login_session.get('gplus_id'):
        del login_session['gplus_id']
    del login_session['email']
    return redirect(url_for('index'))


@app.route('/signup', methods=["POST", "GET"])
def signup():
    """
    Allows a user to register in our system if they dont want to use OAUTH
    """
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        user_email = request.form.get('userEmail')
        user_password1 = request.form.get('userPassword1')
        user_password2 = request.form.get('userPassword2')

        if not user_email or not user_password1 or not user_password2:
            flash("Please fill in all fields")
            return render_template('signup.html')
        if user_password1 != user_password2:
            flash("Passwords do not match")
            return render_template('signup.html')

        current_user = session.query(User).filter_by(email=user_email).first()
        if current_user:
            flash("Account already exists please login")
            return redirect(url_for('showLogin'))

        flash("You have successfully registered")
        user = create_user(email=user_email, password=user_password1)
        login_session['email'] = user.email

        return redirect(url_for('index'))


@app.route('/myAccount', methods=['GET', 'POST'])
@requires_login
def my_account():
    """
    Allows a user to manage their account
    """
    user = get_user(login_session['email'])
    if request.method == 'GET':
        return render_template('myAccount.html', user=user)
    else:
        new_password1 = request.form.get('userPassword1')
        new_password2 = request.form.get('userPassword2')
        if new_password1 != new_password2:
            flash("Passwords do not match!")
            return render_template('myAccount.html', user=user)

        user.hash_password(new_password1)  # set the new password hash
        session.add(user)
        session.commit()
    flash("Your password has been changed.")
    return redirect(url_for('index'))


@app.route("/")
@app.route("/catalog")
def index():
    """
    Main landing page
    """
    categories = session.query(Category).order_by(Category.name).all()
    items = session.query(Item).order_by(Item.created_date.desc()).limit(10)
    return render_template('index.html', categories=categories, items=items)


@app.route("/catalog/<category_name>/items")
@requires_login
def show_category_details(category_name):
    """
    Shows all the categories in our DB
    """
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return render_template('categoryDetails.html', category=category, items=items)


@app.route("/catalog/category/new", methods=["GET", "POST"])
@requires_login
def add_new_category():
    """
    Allows users to add a new category
    """
    if request.method == 'GET':
        return render_template('createCategory.html')
    else:
        user = get_user(login_session['email'])
        category_name = request.form.get('categoryName')
        if not category_name:
            flash("Invalid Category name")
            return render_template('createCategory.html')
        category = session.query(Category).filter_by(name=category_name).first()
        if category:
            flash("Category already exists, the names must be unique")
            return render_template('createCategory.html')

        category = Category(name=category_name, user=user)
        session.add(category)
        session.commit()
        flash("Category {} created!".format(category_name))
        return redirect(url_for('index'))


@app.route("/catalog/<item_id>/details")
def show_item_details(item_id):
    """
    Shows the individual details of a specific item
    """
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('itemDetails.html', item=item, categories=categories)


@app.route("/catalog/<category_name>/add", methods=['POST'])
@requires_login
def add_new_item(category_name):
    """
    Adds a new item to the supplied category
    """
    user = get_user(login_session['email'])
    category = session.query(Category).filter_by(name=category_name).first()
    item_name = request.form.get('itemName')
    item_description = request.form.get('itemDescription')
    if not item_name or not item_description:
        flash("Please fill in all fields")
        return redirect(url_for('show_category_details'), category_name=category_name)

    new_item = Item(name=item_name, description=item_description, category=category, user=user)
    session.add(new_item)
    session.commit()
    flash("New item {} added".format(new_item.name))
    return redirect(url_for('show_category_details', category_name=category_name))


@app.route("/catalog/<category_name>/<item_id>/confirm")
@requires_login
def confirm_delete_item(category_name, item_id):
    """
    Displays the confirmation for deleting an item
    """
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('itemDeleteConfirm.html', item=item)


@app.route("/catalog/<category_name>/<item_id>/delete")
@requires_login
def delete_item(category_name, item_id):
    """
    Performs the actual item delete
    """
    item = session.query(Item).filter_by(id=item_id).one()
    session.delete(item)
    session.commit()
    flash("Item {} deleted".format(item.name))
    return redirect(url_for('show_category_details', category_name=category_name))


@app.route("/catalog/<item_id>/update", methods=['POST'])
@requires_login
def update_item(item_id):
    """
    Updates an item's details such as name, description and category
    """
    item_name = request.form.get('itemName')
    item_description = request.form.get('itemDescription')
    item_category = request.form.get('itemCategory')

    if not item_name or not item_description or not item_category:
        flash("Please fill in all the fields")
        return redirect(url_for('show_item_details', item_id=item_id))

    category = session.query(Category).filter_by(id=item_category).one()
    item = session.query(Item).filter_by(id=item_id).one()
    item.name = item_name
    item.description = item_description
    item.category = category
    session.add(item)
    session.commit()
    flash("Item {} updated".format(item_name))

    # note the item could now be in a new category
    return redirect(url_for('show_category_details', category_name=category.name))


# API end points
@app.route("/api/catalog/category")
def api_get_all_categories():
    """
    returns all categories as JSON
    """
    categories = session.query(Category).all()
    results = [category.serialize for category in categories]
    return jsonify({"categories": results})


@app.route("/api/catalog/category/<category_name>")
def get_category_by_name(category_name):
    """
    Returns the category with the supplied name as JSON
    """
    categories = session.query(Category).filter_by(name=category_name).all()
    results = [category.serialize for category in categories]
    return jsonify({"categories": results})


@app.route("/api/catalog/item")
def api_get_all_items():
    """
    Returns all items as JSON
    """
    items = session.query(Item).all()
    results = [item.serialize for item in items]
    return jsonify({"items": results})


@app.route("/api/catalog/item/<item_name>")
def get_item_by_name(item_name):
    """
    Returns the given items by name (items can share names) as JSON
    """
    items = session.query(Item).filter_by(name=item_name).all()
    results = [item.serialize for item in items]
    return jsonify({"items": results})


def get_user(email):
    """
    Helper to get the user by their email address
    """
    user = session.query(User).filter_by(email=email).first()
    return user


def verify_user(email, password):
    """
    Helpy to verify a user returning the user if they exist or None
    """
    user = session.query(User).filter_by(email=email).first()
    if not user:
        return None
    if not user.verify_password(password):
        return None
    return user


def create_user(email, password=None):
    """
    All users whether they login with OAUTH or a username and password are stored in our DB
    So users entering by Oauth will not have a password, so we create a random one for them
    They can manage their account in "My Account" page if they want supply a password
    """
    new_user = User(email=email)

    if password is None:
        # generate a secret random password for the user who logs in with oauth so we have them in the DB
        password = str(uuid.uuid4().hex)
    new_user.hash_password(password)
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=email).one()
    return user


if __name__ == '__main__':
    app.secret_key = "TODO CHANGE THIS TO TOP SECRET KEY"
    app.run(host="localhost", port=5000, debug=True, threaded=False)
