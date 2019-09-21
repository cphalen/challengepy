from os import path # To check if db file exists
from index import * # for club scraping utility
import sqlite3 # For backend

def db_exists(db_path):
    return path.exists(db_path)

def db_initialize(db_path):
    conn    = sqlite3.connect(db_path)
    cursor  = conn.cursor()

    cursor.execute("""
        CREATE TABLE clubs (clubID INTEGER PRIMARY KEY,
                            name VARCHAR(128),
                            description TEXT);
    """)

    cursor.execute("""
        CREATE TABLE tags (tagID integer primary key,
                           value VARCHAR(128));
    """)

    cursor.execute("""
        CREATE TABLE tagInClub (tagID INTEGER,
                                clubID INTEGER,
                                FOREIGN KEY(tagID) REFERENCES tags(tagID),
                                FOREIGN KEY(clubID) REFERENCES clubs(clubID));
    """)

    clubs              = scrape_club_data()
    club_base          = "INSERT INTO clubs (name, description) VALUES (?, ?)"
    tag_base           = "INSERT INTO tags (value) VALUES (?)"
    tags_in_club_base  = "INSERT INTO TagInClub (tagID, clubID) VALUES (?, ?)"

    for club in clubs:
        cursor.execute(club_base, (club.name, club.description))
        clubID = cursor.lastrowid

        for tag in club.tags:
            cursor.execute(tag_base, (tag,))
            tagID = cursor.lastrowid

            cursor.execute(tags_in_club_base, (tagID, clubID))

    conn.commit()
    return conn


def db_connect(db_path):
    conn = sqlite3.connect(db_path)
    return conn

conn = db_initialize("main.db")
