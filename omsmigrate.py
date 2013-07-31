""" omsmigrate.py | migrating OMS distributorship data to the new handbook
The aim of this script is to migrate distributorship data from OMS over the new handbook.
Particularly we are migrating:
	- Distributorships: each distro will either be made a new team on the handbook,
						or merged with with an existing team
	- Users/Roles: all users will be migrated over, and their roles convereted to new roles,
				   coordinators will be made regular users, and overseers will be made team coordinators
	- Zip Codes: we will also be migrated the assigned zip codes over, with one exception:
				 zip codes associated with a distributorship outside of their geographic range will be
				 moved over to a new city and team. the original coordinators can still request access to
				 contacts in that zip, but we will not be associating contact data with city/teams aside
				 from geographic locality.
"""


import datetime
import logging

from sqlalchemy.orm import scoped_session, sessionmaker, exc
from sqlalchemy import create_engine
from sqlalchemy.schema import ThreadLocalMetaData
from elixir import *

# set up logging
logging.basicConfig(filename="omsmigrate.log", level=logging.DEBUG)
logging.info("\n")
logging.info("** starting new migration: "+str(datetime.datetime.now())+" **")


""" establish multiple database connections (for old and new handbook db)
(loosely) following recipe at: http://elixir.ematia.de/trac/wiki/Recipes/MultipleDatabases
"""

old_engine = create_engine("mysql://bfa:omsoms@localhost:3306/oldhandbook")
old_session = scoped_session(sessionmaker(autoflush=True, bind=old_engine))
old_metadata = metadata
old_metadata.bind = old_engine

new_engine = create_engine("mysql://bfa:omsoms@localhost:3306/newhandbook")
new_session = scoped_session(sessionmaker(autoflush=True, bind=new_engine))
new_metadata = ThreadLocalMetaData()
new_metadata.bind = new_engine