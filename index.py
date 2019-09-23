from flask import Flask, request, render_template, redirect, jsonify, session
from scraper import * # Web Scraping utility functions for Online Clubs with Penn.
from sql import * # Interacting with small database
import bcrypt # For encrypting passwords

app              = Flask(__name__)
app.secret_key   = "LennPabs Secret Klub Key 0047999631_7566378489_6695976906"
DB_PATH          = "main.db"

class Club:
    def __init__(self, name, tags, description):
        self.name        = name
        self.tags        = tags
        self.description = description
        self.is_favorite = False

def scrape_club_data():
    """
    Get club data from legacy website
    """

    html        = get_clubs_html()
    soup        = soupify(html)
    clubs_soup  = get_clubs(soup)
    clubs       = []

    for club_soup in clubs_soup:
        name         = get_club_name(club_soup)
        description  = get_club_description(club_soup)
        tags         = get_club_tags(club_soup)

        clubs.append(Club(name, tags, description))

    return clubs

def get_all_clubs_objects(db):
    """
    Get all clubs from database and format them
    into Club objects so we can post them to front-end
    """

    clubs_list        = db.get_all_clubs()
    clubs             = []
    user              = get_session_username()
    user_favorites    = []

    if (user != None):
        user_favorites = db.get_user_favorites(user)

    for (clubID, name, description) in clubs_list:
        tags = db.get_tags_by_club(clubID)
        club = Club(name, tags, description)

        if (name in user_favorites):
            club.is_favorite = True

        clubs.append(club)

    return clubs

def get_session_username():
    """
    Get username if a user signed in. Otherwise return None.
    """

    if ("username" in session):
        return session["username"]

    return None

# Routes

@app.route('/')
def main():
    db           = Database(DB_PATH)
    location     = {"home": True}
    clubs        = get_all_clubs_objects(db)
    club_count   = len(db.get_all_clubs())

    return render_template('index.html',
                           title='Penn Club Review',
                           user=get_session_username(),
                           club_count=club_count,
                           location=location,
                           clubs=clubs)

@app.route('/login')
def login():
    res        = request.args.get('res')
    try_again  = (res == "noSuchUser")
    location   = {"login": True}
    return render_template('login.html',
                           title='Penn Club Review',
                           user=get_session_username(),
                           location=location,
                           try_again=try_again)

@app.route('/register')
def register():
    location = {"Signin": True}
    return render_template('register.html',
                           title='Penn Club Review',
                           user=get_session_username(),
                           location=location)

@app.route('/submit')
def submit():
    location = {"submit": True}
    return render_template('submit.html',
                           title='Penn Club Review',
                           user=get_session_username(),
                           location=location)

# API

@app.route('/api')
def api():
    return "Welcome to the Penn Club Review API!" + \
                "Please sign in to make full use of the API."

@app.route('/api/clubs', methods=["GET"])
def api_get_clubs():
    if (get_session_username() == None):
        return "API unavailable until you log in!"

    db           = Database(DB_PATH)
    clubs        = db.get_all_clubs()
    clubs_dicts  = list(map(lambda x: {
                                "clubID": x[0],
                                "name": x[1],
                                "description": x[2]
                            }, clubs))

    for club in clubs_dicts:
        tags = db.get_tags_by_club(club["clubID"])
        club["tags"] = tags

    return jsonify({
        "clubs": clubs_dicts
    })

    return redirect("/")

@app.route('/api/clubs', methods=["POST"])
def api_post_clubs():
    if (get_session_username() == None):
        return "API unavailable until you log in!"

    db           = Database(DB_PATH)
    name         = request.form.get("name")
    description  = request.form.get("description")
    tags         = request.form.getlist("listed[]")

    clubID = db.create_club(name, description)
    for tag in tags:
        tagID = db.create_tag(tag)

        # Both IDs are returned in singleton arrays for some reason
        db.create_club_with_tag(tagID[0], clubID[0])

    return redirect("/")

@app.route('/api/login', methods=["POST"])
def api_login():
    db            = Database(DB_PATH)
    username      = request.form.get("username")
    password      = request.form.get("password")
    res           = db.get_salt_hash_by_username(username)

    if (res == []):
        return redirect("/login?res=noSuchUser")

    (salt, hash)  = res[0]
    salt_bytes    = salt.encode("utf-8")
    hash_bytes    = hash.encode("utf-8")
    password_utf  = password.encode("utf-8")
    secret        = bcrypt.hashpw(password_utf, salt_bytes)

    if (hash_bytes == secret):
        session["username"] = username
        return redirect("/")
    else:
        return redirect("/login?res=noSuchUser")

@app.route('/api/register', methods=["POST"])
def api_register():
    db         = Database(DB_PATH)
    username   = request.form.get("username")
    # Text must be uft-8 encoded to be hashed
    password   = request.form.get("password").encode('utf-8')
    salt       = bcrypt.gensalt()
    hash       = bcrypt.hashpw(password, salt)
    # Cannot store bytecode in SQL
    str_salt   = salt.decode("utf-8")
    str_hash   = hash.decode("utf-8")

    db.create_user(username, str_salt, str_hash)
    session["username"] = username

    return redirect("/")

@app.route('/api/logout', methods=["GET", "POST"])
def api_logout():
    del session["username"]
    return redirect("/")

@app.route('/api/current_user')
def api_current_user():
    username     = get_session_username()

    if (username == None):
        return "No user signed in"

    db           = Database(DB_PATH)
    favorites    = db.get_user_favorites(username)

    return jsonify({
        "username": username,
        "favorites": favorites
    })


@app.route('/api/user/<username>')
def api_user(username):
    if (get_session_username() == None):
        return "API unavailable until you log in!"

    db           = Database(DB_PATH)
    is_user      = db.is_user(username)

    if(is_user):
        favorites = db.get_user_favorites(username)

        return jsonify({
            "username": username,
            "favorites": favorites
        })

    else:
        return "No such user"

@app.route('/api/favorite', methods=["POST"])
def api_favorite():
    if (get_session_username() == None):
        return "API unavailable until you log in!"

    db                   = Database(DB_PATH)
    username             = request.form.get("username")
    club                 = request.form.get("club")
    (favorite, clubID)   = db.is_favorite(username, club)

    if (favorite):
        db.delete_favorite(username, clubID)
    else:
        db.create_favorite(username, clubID)

    return redirect("/")

if __name__ == '__main__':
    # Initialize database if not already created
    # Pass in club data so that we can populate the database
    # with club data if it has not been created yet
    db = Database(DB_PATH, clubs_list=scrape_club_data())
    app.run()
