# Penn Labs Server Challenge
Remember to **document your work** in this `README.md` file! Feel free to delete these installation instructions in your fork of this repository.

## Installation
1. Fork + clone this repository.
2. `cd` into the cloned repository.
3. Install `pipenv`
  * `brew install pipenv` if you're on a Mac.
  * `pip install --user --upgrade pipenv` for most other machines.
4. Install packages using `pipenv install`.

## Developing
1. Use `pipenv run python index.py` to run the project.
2. Follow the instructions [here](https://www.notion.so/pennlabs/Server-Challenge-Fall-19-480abf1871fc4a8d9600154816726343).
3. Document your work in the `README.md` file.

## Submitting
Submit a link to your git repository to [this form](https://airtable.com/shrqdIzlLgiRFzEWh) by 11:59pm on Monday, September 23rd.

## Installing Additional Packages
To install additional packages run `pipenv install <package_name>` within the cloned repository.

## API

#### api/clubs
Here, with a `GET` request you will get to see all registered clubs, their
descriptions, and their associated tags. With a `POST` request you will be
able to create a new club if you specify the parameters
```
name: club name
description: club description
```
You can also do this through the front-end.

#### api/login
Here you can log into an existing user account. Provided the account already
exists, you need only specify the following parameters. If the account
does not exist, you will be direct to `/register` to create an account.
```
username: username
password: password
```
fairly straightfoward ;)

#### api/register
Here you can create a new user account. You only need to specify
```
username: username
password: password
```
I'm gonna expose myself and point out that because `Sqlite3` is weird with
`INSERT IGNORE` statements. `SQL Alchemy` didn't actually let me write
any `INSERT IGNORE` statements, so if you create duplicate users you will
likely get an error because `username` is the `primary key` in the table.

#### api/logout
By far my favorite API call in the entire program. Takes no parameters and
simply logs a user out of the `session` variable if there is a user in there.

### api/user/:username
This API call returns user data for the user specified in the route parameter.
If no such user exists, then API will tell you so. Otherwise, it will give
you the users favorited clubs as well as their user name. Not their salt
or hash though as that would obviously be a security breach!

### api/favorite
Creates a new favorite relationship between a user and a club. If you provide
```
username: username
clubID: clubID
```
the API call will insert a new row into favorite.

## Added Features

### Front-end
The project has a fairly extensive front-end that could definitely benefit
from a design rework! To name a few key features though -- you can add clubs,
register users, log into users, favorite clubs, unfavorite clubs, view clubs,
and search for clubs all through the front-end.

### Database
I'm not sure if Sqlite3 was necessarily the best idea, and certainly would
not be the best move if we were going to scale the app, but at least for
the initial POC it works well -- the SQL Alchemy code could also easily
be ported over to MySQL or any other SQL client. In the `sql.py` file you
can view a lot of the database functionality. Here's a TL;DR of the database
schema (not a full ERD though!)

```
CREATE TABLE clubs (
	clubID INTEGER NOT NULL,
	name VARCHAR,
	description VARCHAR,
	PRIMARY KEY ("clubID")
);
CREATE TABLE tags (
	tagID INTEGER NOT NULL,
	value VARCHAR,
	PRIMARY KEY ("tagID")
);
CREATE TABLE users (
	username VARCHAR NOT NULL,
	salt VARCHAR,
	hash VARCHAR,
	PRIMARY KEY (username)
);
CREATE TABLE clubWithTag (
	tagID INTEGER,
	clubID INTEGER,
	FOREIGN KEY("tagID") REFERENCES tags ("tagID"),
	FOREIGN KEY("clubID") REFERENCES clubs ("clubID")
);
CREATE TABLE favorite (
	username VARCHAR,
	clubID INTEGER,
	FOREIGN KEY(username) REFERENCES users (username),
	FOREIGN KEY("clubID") REFERENCES clubs ("clubID")
);
```
All of the functionality for interacting with the database in implemented
in `sql.py` through the `Database` class. Check out the instance functions
for `Database` -- this is the only place in the program that we ever interact
with the database! So you know where to look if you have questions.

### Users
The app requires the creation of user accounts to access the API. To create
a user you can use the front-end or the API. The Flask app will store your
username in the `session` variable. While signed in, you can favorite clubs
which are then favorited specifically to your account. Also, you can create
clubs. You stay signed in until the `session` dies or until you manually
log out.

> Note that the user _jen_ has still been inserted directly into the database,
  she has been given the password _LennPabs_. Sign in to her account
  if you want!

## Areas for Improvement (left incomplete because of the time constraint)

* General bug testing would be wonderful -- I'm positive there are issues.
* End-to-end API testing suite. A test program that creates a new user,
  logs them in, creates a new club, checks that the club exists, check that the
  user exists, favorites a new club, etc. Then, also automates the checking
  front-end process to back sure both the back-end API and front-end are
  in sync.
* Efficiency across the board. The program was developed for functionality
  but not necessarily performance. There are definitely areas that
  do not exercise best practice in maximizing efficiency.
* Editing clubs once created -- also associated clubs with users who created
  the club so that only users who created a club could modify that given club.
* Refactoring -- lots of code is repeated. Namely, there is a lot of code
  in `index.py` that should probably be moved to `sql.py` to avoid repetition.
