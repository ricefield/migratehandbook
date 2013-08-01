""" hbmigratenew.py | this doesn't even merit documentation

lol.
"""

import datetime
import logging

from sqlalchemy.orm import scoped_session, sessionmaker, exc
from sqlalchemy import create_engine
from sqlalchemy.schema import ThreadLocalMetaData
from elixir import *

# these are the cities to be migrated and a mapping of their ids from old->new
cities = dict(72=,  # jacksonville, FL
			  63=,  # round rock, TX
			  41=23,  # lake forest, CA
			  59=5,   # knoxville, TN
			  47=30)  # palatine, IL

""" establish multiple database connections (for old and new handbook db)
(loosely) following recipe at: http://elixir.ematia.de/trac/wiki/Recipes/MultipleDatabases
"""

old_engine = create_engine("mysql://bfa:gtca@localhost:5432/oldhandbook")
old_session = scoped_session(sessionmaker(autoflush=True, bind=old_engine))
old_metadata = metadata
old_metadata.bind = old_engine

new_engine = create_engine("mysql://bfa:gtca@localhost:5432/newhandbook")
new_session = scoped_session(sessionmaker(autoflush=True, bind=new_engine))
new_metadata = ThreadLocalMetaData()
new_metadata.bind = new_engine

""" model scaffolding """

# old
class CitiesOld(Entity):
	""" oldhandbook/cities """
	using_options(metadata=old_metadata, session=old_session, tablename="cities", autoload=True)


""" migration """

for city in cities:
