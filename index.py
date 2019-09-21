from flask import Flask, request
from scraper import * # Web Scraping utility functions for Online Clubs with Penn.
app = Flask(__name__)

class Club:
    def __init__(self, name, tags, description):
        self.name        = name
        self.tags        = tags
        self.description = description

@app.route('/')
def main():
    return "Welcome to Penn Club Review!"

@app.route('/api')
def api():
    return "Welcome to the Penn Club Review API!."

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


if __name__ == '__main__':
    app.run()
    scrape_club_data()
