from flask import Flask, request, render_template
from scraper import * # Web Scraping utility functions for Online Clubs with Penn.
from sql import * # Interacting with small database
app = Flask(__name__)

import sys

DB_PATH = "main.db"

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

# Routes

@app.route('/')
def main():
    location = {"home": True}
    clubs = scrape_club_data()
    return render_template('index.html',
                           title='Penn Club Review',
                           club_count=241,
                           location=location,
                           clubs=clubs)

@app.route('/add')
def add():
    location = {"add": True}
    return render_template('index.html',
                           title='Penn Club Review',
                           club_count=241,
                           location=location,
                           clubs=clubs)

@app.route('/login')
def login():
    location = {"login": True}
    return render_template('index.html',
                           title='Penn Club Review',
                           club_count=241,
                           location=location,
                           clubs=clubs)

@app.route('/api/add')
def api():
    return "Welcome to the Penn Club Review API!."
#
# @app.route('/api')
# def api():
#     return "Welcome to the Penn Club Review API!."


if __name__ == '__main__':
    app.run()

    if (db_exists(DB_PATH)):
        conn = db_connect(DB_PATH)
    else:
        conn = db_initialize(DB_PATH)
