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

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.schema import ThreadLocalMetaData
from elixir import *


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

""" MODEL DATA:
	before we can begin doing anything, we need to first model all the tables we'll be dealing with
"""

""" model team and city data
	old handbook:
		- cities
	new handbook:
		- bf_city
		- bf_team
		- bf_team_members
"""

# old
class CitiesOld(Entity):
	""" oldhandbook/cities """
	using_options(metadata=old_metadata, session=old_session, tablename="cities", autoload=True)

## TODO: teams, user association to teams

# new
class CityNew(Entity):
	""" newhandbook/bf_city """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_city", autoload=True)

class TeamNew(Entity):
	""" newhandbook/bf_team """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_team", autoload=True)

class TeamMembersNew(Entity):
	""" newhandbook/bf_team_members """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_team_members", autoload=True)

""" model user data
	old handbook:
		- users
	new handbook:
		- bf_users
		- bf_user_meta (stores extra misc. data about users)
"""

# old
class UsersOld(Entity):
	""" oldhandbook/users """
	using_options(metadata=old_metadata, session=old_session, tablename="users", autoload=True)

## TODO: user permissions/roles
### RESOLVED: roles are in user table: admin_role, teamcoordinator_role, and teammember_role columns

# new
class UsersNew(Entity):
	""" newhandbook/bf_users """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_users", autoload=True)

class UserMetaNew(Entity):
	""" newhandbook/bf_user_meta """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_user_meta", autoload=True)

""" model contact data
	old handbook:
		- contacts
		- contacts_users
		- bfa_recipients
		- bfa_contacts
		- bfa_contacts_users
	new handbook:
		- bf_oms_contacts
		- bf_contacts
		- bf_contacts_members
"""

# old
class ContactsOld(Entity):
	""" oldhandbook/contacts """
	using_options(metadata=old_metadata, session=old_session, tablename="contacts", autoload=True)

class ContactsUsersOld(Entity):
	""" newhandbook/contacts_users """
	using_options(metadata=old_metadata, session=old_session, tablename="contacts_users", autoload=True)

class BFARecipientsOld(Entity):
	using_options(metadata=old_metadata, session=old_session, tablename="bfa_recipients", autoload=True)

class BFAContactsOld(Entity):
	using_options(metadata=old_metadata, session=old_session, tablename="bfa_contacts", autoload=True)

class BFAContactsUsersOld(Entity):
	using_options(metadata=old_metadata, session=old_session, tablename="bfa_contacts_users", autoload=True)

# new
class OMSContactsNew(Entity):
	using_options(metadata=new_metadata, session=new_session, tablename="bf_oms_contacts", autoload=True)

class ContactsNew(Entity):
	using_options(metadata=new_metadata, session=new_session, tablename="bf_contacts", autoload=True)

class ContactsMembersNew(Entity):
	using_options(metadata=new_metadata, session=new_session, tablename="bfa_contacts_users", autoload=True)

""" model contact comment data
	old handbook:
		- comments
	new handbook:
		- bf_contacts_comments
"""
# old
class CommentsOld(Entity):
	""" oldhandbook/comments """
	using_options(metadata=old_metadata, session=old_session, tablename="comments", autoload=True)

# new
class ContactsCommentsNew(Entity):
	""" newhandbook/bf_contacts_comments """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_contacts_comments", autoload=True)

""" MIGRATION: 
	after modeling all the necessary tables, we can begin migrating data
"""

# setup and create the tables so we can begin migrating data
create_all()
setup_all()


""" migrate team and city data
"""

""" migrate user accounts
"""

""" migrate contacts
"""

""" migrate contact comments
"""



