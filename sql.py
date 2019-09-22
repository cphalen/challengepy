from os import path # To check if db file exists
from sqlalchemy import *
import sys

class Database:
    def __init__(self, db_path, clubs_list):
        """
        Initialize SQL Alchemcy engine object that will store
        all of our SQL data.
        """

        db_exists         = not path.exists(db_path)
        self.db_path      = db_path
        self.engine       = create_engine('sqlite:///' + db_path)
        self.connection   = self.engine.connect()
        self.metadata     = MetaData()

        if (db_exists):
            self.initialize(clubs_list)
        else:
            self.clubs = Table('clubs',
                                self.metadata,
                                autoload=True,
                                autoload_with=self.engine)

            self.tags = Table('tags',
                               self.metadata,
                               autoload=True,
                               autoload_with=self.engine)

            self.clubWithTag = Table('clubWithTag',
                                      self.metadata,
                                      autoload=True,
                                      autoload_with=self.engine)

            self.users = Table('users',
                                self.metadata,
                                autoload=True,
                                autoload_with=self.engine)

            self.favorite = Table('favorite',
                                  self.metadata,
                                  autoload=True,
                                  autoload_with=self.engine)

    def initialize(self, clubs_list):
        """
        Initialize all tables in SQL database

        clubs        : stores all club data
        tags         : stores data for a tag associated with a club
        clubWithTag  : relationship between club and tag (many-to-many)
        users        : stores user data
        favorite     : stores which user has favorited which
                       clubs (one-to-many)
        """

        self.clubs = Table(
           'clubs', self.metadata,
           Column('clubID', Integer, primary_key=True),
           Column('name', String),
           Column('description', String)
        )

        self.tags = Table(
           'tags', self.metadata,
           Column('tagID', Integer, primary_key=True),
           Column('value', String)
        )

        self.clubWithTag = Table(
           'clubWithTag', self.metadata,
           Column('tagID', Integer, ForeignKey('tags.tagID')),
           Column('clubID', Integer, ForeignKey('clubs.clubID'))
        )

        self.users = Table(
           'users', self.metadata,
           Column('username', String, primary_key=True),
           Column('salt', String),
           Column('hash', String)
        )

        self.favorite = Table(
           'favorite', self.metadata,
           Column('username', String, ForeignKey('users.username')),
           Column('clubID', Integer, ForeignKey('clubs.clubID'))
        )

        self.metadata.create_all(self.engine)
        clubs_list = clubs_list

        for club in clubs_list:
            query   = insert(self.clubs).values(name=club.name,
                                                description=club.description)
            result  = self.connection.execute(query)
            clubID  = result.inserted_primary_key

            for tag in club.tags:
                query   = insert(self.tags).values(value=tag)
                result  = self.connection.execute(query)
                tagID   = result.inserted_primary_key

                # Both IDs are returned in singleton arrays for some reason
                query   = insert(self.clubWithTag).values(tagID=tagID[0],
                                                        clubID=clubID[0])
                result  = self.connection.execute(query)

    def create_user(self, username, salt, hash):
        """
        Register a new user in the backend

        username   : their username
        salt       : string for bytecode used to salt the password
        hash       : resulting hash after hashing the password
        """

        query   = insert(self.users).values(username=username,
                                            salt=salt,
                                            hash=hash)
        result  = self.connection.execute(query)

    def get_user(self, username, hash):
        """
        Returns username and a list of that users favorite clubs
        """
        query   = select([self.users]) \
                    .where(self.users.columns.username == username,
                           self.users.columns.hash == hash)
        result  = self.connection.execute(query)
        return result.fetchall()

    def is_user(self, username):
        """
        Check to see if a user exists in the databas
        """

        query   = select([self.users]) \
                    .where(self.users.columns.username == username)
        result  = self.connection.execute(query)
        return len(result.fetchall()) != 0

    def create_club(self, name, description):
        """
        Registers a new club in the database. This is done independetly
        of registering which tags are associated with the given club.
        Look in `index` to find implementation of how clubs are
        inserted simultaneously with tags
        """

        query   = insert(self.clubs).values(name=name,
                                            description=description)
        result  = self.connection.execute(query)
        return result.inserted_primary_key

    def get_club(self, name):
        """
        Returns data on a given club searching by name
        """

        query   = select([self.users]) \
                    .where(self.clubs.columns.name == name)
        result  = self.connection.execute(query)
        return result.fetchall()

    def create_tag(self, value):
        """
        Registers a new tag in the database. The tag will have
        the value as well as a tagID as the value is not necessarily
        unqiue. There is no INSERT IGNORE in Sqlite3, so we may have
        duplicate entries, but perhaps that's an issue to be resolved
        in a later rendition
        """
        query   = insert(self.tags).values(value=value)
        result  = self.connection.execute(query)
        return result.inserted_primary_key

    def create_club_with_tag(self, tagID, clubID):
        """
        Inserts a new relationship between club and tag. This is how each
        tag is associated with each club.
        """
        query   = insert(self.clubWithTag).values(tagID=tagID, clubID=clubID)
        result  = self.connection.execute(query)

    def get_all_clubs(self):
        """
        Returns a list of all clubs. Used in counting the number of current
        clubs
        """
        query   = select([self.clubs])
        result  = self.connection.execute(query)
        return result.fetchall()


    def get_clubs_by_tag(self, tag):
        """
        This function is unused but still implemented. It provides the
        clubs that have a given tag, in case one day you wanted to
        implement searching by tag
        """

        joined  = self.clubs.join(self.clubWithTag,
                                  self.clubs.columns.clubID == \
                                  self.clubWithTag.columns.clubID) \
                            .join(self.tags,
                                  self.clubWithTag.columns.tagID == \
                                  self.tags.columns.tagID)

        query   = select([joined]).where(self.tags.columns.value == tag)
        result  = self.connection.execute(query)
        return result.fetchall()

    def get_tags_by_club(self, clubID):
        """
        This actually is used when we print all new clubs to index.htmt.
        We have to know what clubs are associated with each club when
        creating the template for the front-end club cards
        """

        joined  = self.tags.join(self.clubWithTag,
                                 self.tags.columns.tagID == \
                                 self.clubWithTag.columns.tagID) \

        query   = select([joined]) \
                    .where(self.clubWithTag.columns.clubID == clubID)
        result  = self.connection.execute(query)
        return list(map(lambda x: x[1], result.fetchall()))

    def create_favorite(self, username, clubID):
        """
        Insert new row into favorite.
        """

        query   = insert(self.favorite).values(clubID=clubID,
                                               username=username)
        result  = self.connection.execute(query)

    def delete_favorite(self, username, clubID):
        """
        Delete existing from favorite.
        """
        query   = delete(self.favorite) \
                    .where(self.favorite.columns.clubID == clubID and \
                           self.favorite.columns.username == username)
        result  = self.connection.execute(query)

    def is_favorite(self, username, club):
        """
        See if a given club is already favorited by a given user. If the club
        is already favorited, then this call is supposed to unfavorite.
        However, if the clbu is not already favorited, then this call
        is meant for us to favorite the club.

        Also, returns the clubID so either `create_favorite` or
        `delete_favorite` (whichever we decide to call) doesn't have to search
        for it again
        """

        query      = select([self.clubs.columns.clubID]) \
                        .where(self.clubs.columns.name == club) \
                        .distinct()
        result     = self.connection.execute(query)
        (clubID,)  = result.fetchall()[0]

        query     = select([self.favorite]) \
                        .where(self.favorite.columns.clubID == clubID and \
                               self.favorite.columns.username == username)
        result    = self.connection.execute(query)
        favorite  = len(result.fetchall()) != 0

        return (favorite, clubID)

    def get_user_favorites(self, username):
        """
        Get all of a users favorite clubs by club name.
        """

        joined  = self.clubs.join(self.favorite,
                                  self.clubs.columns.clubID == \
                                  self.favorite.columns.clubID)

        query   = select([joined]) \
                    .where(self.favorite.columns.username == username)
        result  = self.connection.execute(query)

        # Map across to extract club name from each row
        return list(map(lambda x: x[1], result.fetchall()))

    def get_salt_hash_by_username(self, username):
        """
        For login we need a users salt and hash to check if the password
        they provided is correct. This function takes a username and returns
        the associated salt and hash if they exist.
        """

        query   = select([self.users.columns.salt, self.users.columns.hash]) \
                    .where(self.users.columns.username == username)
        result  = self.connection.execute(query)
        return result.fetchall()
