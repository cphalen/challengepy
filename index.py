from flask import Flask, request, render_template, redirect
from scraper import * # Web Scraping utility functions for Online Clubs with Penn.
from sql import * # Interacting with small database
import bcrypt # For encrypting passwords

app       = Flask(__name__)
DB_PATH   = "main.db"

class Club:
    def __init__(self, name, tags, description):
        self.name        = name
        self.tags        = tags
        self.description = description

def scrape_club_data():
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
    clubs_list = db.get_all_clubs()
    clubs = []

    for (clubID, name, description) in clubs_list:
        tags = db.get_tags_by_club(clubID)
        clubs.append(Club(name, tags, description))

    return clubs

# Routes

@app.route('/')
def main():
    db           = Database(DB_PATH, scrape_club_data())
    location     = {"home": True}
    clubs        = get_all_clubs_objects(db)
    club_count   = len(db.get_all_clubs())
    return render_template('index.html',
                           title='Penn Club Review',
                           club_count=club_count,
                           location=location,
                           clubs=clubs)

@app.route('/submit')
def submit():
    location = {"submit": True}
    return render_template('submit.html',
                           title='Penn Club Review',
                           location=location)

@app.route('/login')
def login():
    location = {"login": True}
    return render_template('login.html',
                           title='Penn Club Review',
                           location=location)

@app.route('/api/submit', methods=["POST"])
def api_submit():
    db           = Database(DB_PATH, scrape_club_data())
    name         = request.form.get("name")
    description  = request.form.get("description")
    tags         = request.form.getlist("listed[]")

    clubID = db.create_club(name, description)
    for tag in tags:
        tagID = db.create_tag(tag)

        # Both IDs are returned in singleton arrays for some reason
        db.create_club_with_tag(tagID[0], clubID[0])

    return redirect("/")

@app.route('/api/register', methods=["POST"])
def api_register():
    db         = Database(DB_PATH, scrape_club_data())
    username   = request.form.get("username")
    password   = request.form.get("password")
    salt       = bcrypt.gensalt()
    hash       = bcrypt.hashpw(passwd, salt)

    db.create_user(email, salt, hash)
    return redirect("/")

@app.route('/api')
def api():
    return "Welcome to the Penn Club Review API!."

if __name__ == '__main__':
    # Initialize database if not already created
    db = Database(DB_PATH, scrape_club_data())
    app.run()
