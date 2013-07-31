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
logging.info("** starting new OMS migration: "+str(datetime.datetime.now())+" **")


""" establish multiple database connections (for old and new handbook db)
(loosely) following recipe at: http://elixir.ematia.de/trac/wiki/Recipes/MultipleDatabases
"""

old_engine = create_engine("mysql://bfa:omsoms@localhost:3306/dbo")
old_session = scoped_session(sessionmaker(autoflush=True, bind=old_engine))
old_metadata = metadata
old_metadata.bind = old_engine

new_engine = create_engine("mysql://bfa:omsoms@localhost:3306/newhandbook")
new_session = scoped_session(sessionmaker(autoflush=True, bind=new_engine))
new_metadata = ThreadLocalMetaData()
new_metadata.bind = new_engine

""" MODEL DATA:
	before we can begin doing anything, we need to first model all the tables we'll be dealing with
"""

# old
class Distributorship(Entity):
	""" dbo/distributorship """
	using_options(metadata=old_metadata, session=old_session, tablename="distributorship", autoload=True)

class DistributorshipUserInRole(Entity):
	""" dbo/distributorshipuserinrole """
	using_options(metadata=old_metadata, session=old_session, tablename="distributorshipuserinrole", autoload=True)

class DistributorshipZipCode(Entity):
	""" dbo/distributorzipcode """
	using_options(metadata=old_metadata, session=old_session, tablename="distributorshipzipcode", autoload=True)

# new
class City(Entity):
	""" newhandbook/bf_city """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_city", autoload=True)

class ZipCode(Entity):
	""" newhandbook/bf_zipcode """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_zipcode", autoload=True)

class CityZipCodes(Entity):
	""" newhandbook/bf_city_zipcodes """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_city_zipcodes", autoload=True)

class Team(Entity):
	""" newhandbook/bf_team """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_team", autoload=True)

class Users(Entity):
	""" newhandbook/bf_users """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_users", autoload=True)

class UserMeta(Entity):
	""" newhandbook/bf_user_meta """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_user_meta", autoload=True)

class TeamMembers(Entity):
	""" newhandbook/bf_team_members """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_team_members", autoload=True)

# setup and create the tables so we can begin migrating data
setup_all()
create_all()

logging.info("### successfully generated Python models ###")


""" MIGRATION """

logging.info("### beginning migration of data ###")

distro2city = {}
distro2team = {}


def check_duplicate(distro, hbcity):
	""" takes a distributorship name from the oms and checks to see
	if there's an identical city in the handbook
	"""
	try:
		city, state = distro.split()
		if 
	except ValueError:
		return True


for distro in Distributorship.query.all():
	if # not duplicate:

		# migrate distributorship -> city, team
		city, state = distro.Name.split()

		# create city
		newcity = City(city_name=city, city_state=state)
		newcity.city_description = ""
		new_session.add(newcity)
		new_session.commit()

		# create team
		newteam = TeamNew(team_name=city.name+", "+city.state, 
						  team_assigned_city=newcity.city_id)
		new_session.add(newteam)
		new_session.commit()

		# mappings
		distroy2city[distro.Id] = newcity.city_id
		distro2team[distro.Id] = newteam.team_id

		# migrate zip code assignments
		for row in DistributorshipZipCode.query.filter_by(DistributorshipId=distro.Id).all():
			# find zipcodes and create zipcode relationships
			newzip = CityZipCodes(city_id=newcity.city_id,
								 	 city_group_id=None,
									 zipcode_id=ZipCode.query.filter_by(zip_code=row.Zipcode).one().id,
									 zipcode=row.Zipcode,
									 type=1)
			new_session.add(newzip)
			new_session.commit()

		# create new users and roles
		for user in DistributorshipUserInRole.filter_by(DistributorshipId=distro.Id).all():

			# create new user
			newuser = UsersNew(email=user.Username,
							   username=user.Username,
							   created_on=datetime.datetime.now(),
							   display_name=""
			newuser.password_hash = "" # null, necessitates a reset
			newuser.salt = "" # see above
			# necessary bc new db doesn't allow NULL for this value
			newuser.last_ip = ""
			newuser.active = 1 # user shouldn't have to activate
			newuser.activate_hash = "" # shouldn't be necessary
			
			# user permissions
			if user.Role == 'Overseer':
				newuser.role_id = 7
			else:
				newuser.role_id = 4

			# commit 
			new_session.add(newuser)
			new_session.commit()

	else:
		# what to do if there's a duplicate?


