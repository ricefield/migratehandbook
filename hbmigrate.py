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

class ZipCodeNew(Entity):
	""" newhandbook/bf_zipcode """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_zipcode", autoload=True)

class CityZipCodesNew(Entity):
	""" newhandbook/bf_city_zipcodes """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_city_zipcodes", autoload=True)

class TeamNew(Entity):
	""" newhandbook/bf_team """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_team", autoload=True)

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

class TeamMembersNew(Entity):
	""" newhandbook/bf_team_members """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_team_members", autoload=True)

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
setup_all()
create_all()


""" migrate team and city data
	- create new cities and teams
	- transfer city name and state
	- establish foreign-key relationship between teams and cities
	- the rest is default or null-allowed values
"""

city2city = {} # a mapping of old city ids to new city ids
city2team = {} # a mapping of old city ids to new team ids

for city in CitiesOld.query.all():
	# create city
	newcity = CityNew(city_name=city.name, 
					  city_state=city.state)
	newcity.city_description = ""
	new_session.add(newcity)
	new_session.commit()
	city2city[city.id] = newcity.city_id

	# find zipcodes and create zipcode relationships
	for zipcode in ZipCodeNew.query.filter_by(city=newcity.city_name).all():
		newzip = CityZipCodesNew(city_id=newcity.city_id,
							 	 city_group_id=None,
								 zipcode_id=zipcode.id,
								 zipcode=zipcode.zip_code,
								 type=1)
		new_session.add(zipcode)
		new_session.commit()


	# create team
	newteam = TeamNew(team_name=city.name+", "+city.state, 
					  team_assigned_city=newcity.city_id)
	new_session.add(newteam)
	new_session.commit()
	city2team[city.id] = newteam.team_id 

""" migrate user accounts
	- create new user accounts
	- fill in basic info, rest is defaults or null-allowed values
	- migrate permissions
	- dump gender, age, cellphone, homephone, dob, locality, socialcast data, and bfa_access in bf_user_meta
	- associate with teams
"""

user2user = {} # a mapping of old user ids to new user ids

for user in UsersOld.query.all():
	newuser = UsersNew(email=user.email,
					   username=user.first_name.lower()+user.last_name.lower()
					   created_on=user.created_at
					   display_name=user.first_name+" "+user.last_name)
	newuser.password_hash = "" # null, necessitates a reset
	newuser.salt = "" # see above
	# necessary bc new db doesn't allow NULL for this value
	newuser.last_ip = user.last_sign_in_ip if user.last_sign_in_ip is not None else ""
	newuser.active = 1 # user shouldn't have to activate
	newuser.activate_hash = "" # shouldn't be necessary
	
	# user permissions
	if user.teamcoordinator_role == 1:
		newuser.role_id = 7
	elif user.admin_role == 1:
		newuser.role_id = 1
	else:
		newuser.role_id = 4

	# commit so we can get newuser's id
	new_session.add(newuser)
	new_session.commit()

	# build mapping
	user2user[user.id] = newuser.id

	# user meta
	meta = {
		"gender": user.gender,
		"age": user.age,
		"cellphone": user.cellphone,
		"homephone": user.homephone,
		"dob": user.dob,
		"locality": user.locality,
		"socialcast_url": user.socialcast_url,
		"socialcast_group": 0 if user.socialcast_group is not 1 else 1
		"bfa_approved": 0 if user.bfa_access is not 1 else 1
	}
	for key, value in meta.iteritems():
		newusermeta = UserMetaNew(user_id=newuser.id,
								  meta_key=key,
								  meta_value=str(value))
		new_session.add(newusermeta)
		new_session.commit()

	# associate new users to teams
	newteammember = TeamMembersNew(user_id=newuser.id, 
				   				   team_id=city2team[user.city_id],
								   role=0, # QUESTION!! 1 or 0 only?? what does these values represent
				   				   label="",
				   				   active=1,
				   				   active_team=1,
				   				   bfa_approved=0 if user.bfa_access is not 1 else 1)
	new_session.add(newteammember)
	new_session.commit()

""" migrate contacts
"""

""" migrate contact comments
"""



