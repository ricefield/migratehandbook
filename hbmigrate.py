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

""" establish database connections
