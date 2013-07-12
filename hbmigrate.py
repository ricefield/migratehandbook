""" migrate.py | a tool for migrating the GTCA handbooks

This script migrates data from the old GTCA handbook to the new one.
As the new handbook nears completion, we want to migrate teams still using the old handbook to the new one.

In this script, we deal primarily with: 
	teams
	users (team members)
	contacts
	contact comments.
Additionally, we take care of relationships between these entities:
	teams and users
	contacts and users
	contact and comments
	comments and users

SQLAlchemy and Elixir (a wrapper for SQLAlchemy) are used to programmatically interface with MySQL in native Python.
Check requirements.txt for other dependencies. 

"""

from sqlalchemy import *
from elixir import *


""" establish multiple database connections (for old and new handbook db)
(loosely) following recipe at: http://elixir.ematia.de/trac/wiki/Recipes/MultipleDatabases
"""

old_engine = create_engine("mysql://bfa:gtca@localhost:5432/oldhandbook")
old_session = scoped_session(sessionmaker(autoflush=True, transactional=True, bind=old_engine))
old_metadata = metadata
old_metadata.bind = old_engine

new_engine = create_engine("mysql://bfa:gtca@localhost:5432/newhandbook")
new_session = scoped_session(sessionmaker(autoflush=True, transactional=True, bind=new_engine))
new_metadata = metadata
new_metadata.bind = new_engine