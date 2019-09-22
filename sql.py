from os import path # To check if db file exists
from sqlalchemy import *
import sys

class Database:
    def __init__(self, db_path, clubs_list):
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

    def initialize(self, clubs_list):

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
           Column('salt', Integer),
           Column('hash', String)
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
        query   = insert(self.clubs).values(username=username,
                                            salt=salt,
                                            hash=hash)
        result  = self.connection.execute(query)

    def get_user(self, username, hash):
        query   = select([self.users]) \
                    .where(self.users.columns.username == username,
                           self.users.columns.hash == hash)
        result  = self.connection.execute(query)
        return result.fetchall()

    def create_club(self, name, description):
        query   = insert(self.clubs).values(name=name,
                                            description=description)
        result  = self.connection.execute(query)
        return result.inserted_primary_key

    def get_club(self, name):
        query   = select([self.users]) \
                    .where(self.clubs.columns.name == name)
        result  = self.connection.execute(query)
        return result.fetchall()

    def create_tag(self, value):
        query   = insert(self.tags).values(value=value)
        result  = self.connection.execute(query)
        return result.inserted_primary_key

    def create_club_with_tag(self, tagID, clubID):
        query   = insert(self.clubWithTag).values(tagID=tagID, clubID=clubID)
        result  = self.connection.execute(query)

    def get_all_clubs(self):
        query   = select([self.clubs])
        result  = self.connection.execute(query)
        return result.fetchall()


    def get_clubs_by_tag(self, tag):
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
        joined  = self.tags.join(self.clubWithTag,
                                 self.tags.columns.tagID == \
                                 self.clubWithTag.columns.tagID) \

        query   = select([joined]) \
                    .where(self.clubWithTag.columns.clubID == clubID)
        result  = self.connection.execute(query)
        return list(map(lambda x: x[1], result.fetchall()))
