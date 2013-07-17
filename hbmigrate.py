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

## NOTE: in order for this script to work, you have to add primary key's to three tables:
# oldhandbook/bfa_contacts_users, oldhandbook/contacts_users, and oldhandbook/bfa_recipients


from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.schema import ThreadLocalMetaData
from elixir import *
import datetime


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
	""" oldhandbook/contacts_users """
	using_options(metadata=old_metadata, session=old_session, tablename="contacts_users", autoload=True)

class BFARecipientsOld(Entity):
	""" oldhandbook/bfa_recipients """
	using_options(metadata=old_metadata, session=old_session, tablename="bfa_recipients", autoload=True)

class BFAContactsOld(Entity):
	""" oldhandbook/bfa_contacts """
	using_options(metadata=old_metadata, session=old_session, tablename="bfa_contacts", autoload=True)

class BFAContactsUsersOld(Entity):
	""" oldhandbook/bfa_contacts_users """
	using_options(metadata=old_metadata, session=old_session, tablename="bfa_contacts_users", autoload=True)

# new
class OMSContactsNew(Entity):
	""" newhandbook/bf_oms_contacts """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_oms_contacts", autoload=True)

class ContactsNew(Entity):
	""" newhandbook/bf_contacts """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_contacts", autoload=True)

class ContactsMembersNew(Entity):
	""" newhandbook/bf_contact_members """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_contact_members", autoload=True)

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


################################################################


""" MIGRATION: 
	after modeling all the necessary tables, we can begin migrating data
"""

# setup and create the tables so we can begin migrating data
setup_all()
create_all()


""" migrate team and city data
	- create new cities and teams
	- find zipcodes and establish zipcode relationships
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
	# create new user
	newuser = UsersNew(email=user.email,
					   username=user.first_name.lower()+user.last_name.lower(),
					   created_on=user.created_at,
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
		"socialcast_group": 0 if user.socialcast_group is not 1 else 1,
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
								   role=1 if newuser.role_id is not 4 else 0,
				   				   label="",
				   				   active=1,
				   				   active_team=1,
				   				   bfa_approved=0 if user.bfa_access is not 1 else 1)
	new_session.add(newteammember)
	new_session.commit()

""" migrate contacts
	- create new contacts from contacts and bfa contacts, up to a year old

"""

contact2contact = {} # mapping of old (non-bfa) contacts to new contacts
bfacontact2contact = {} # mapping of old bfa contacts to new contacts

# old contacts -- only import those within the past year
for contact in ContactsOld.query.filter(ContactsOld.datemet > datetime.date.today() - datetime.timedelta(365)):
	# create new contact
	newcontact = ContactsNew(team_id=city2team[contact.city_id],
							 contacts_firstname=contact.first_name,
							 contacts_lastname=contact.last_name,
							 contacts_email=contact.email,
							 contacts_phone=contact.phone,
							 contacts_gender=contact.gender,
							 contacts_address=contact.address,
							 contacts_city=contact.addr_city,
							 contacts_state=contact.state,
							 contacts_zip=contact.zip,
							 date_met=contact.datemet,
							 customer_id="")
	new_session.add(newcontact)
	new_session.commit()

	# build mapping
	contact2contact[contact.id] = newcontact.contact_id

# create contact to user relationships
for row in ContactsUsersOld.query.all():
	newcontactmember = ContactsMembersNew(contact_id=contact2contact[row.contact_id], member_id=user2user[row.user_id])  # which is this? 

# old bfa contacts -- only import those within the past year AND have a user assigned
for row in BFAContactsUsersOld.query.all():
	if BFAContactsOld.query.filter_by(id=row.bfa_contact_id).one().date > (datetime.date.today() - datetime.timedelta(365)):
		# create new contact
		bfacontact = BFAContactsOld.query.filter_by(id=row.bfa_contact_id).one()
		newcontact = ContactsNew(team_id=city2team[user2user[row.user_id]],
								 contacts_firstname=bfacontact.first_name,
								 contacts_lastname=bfacontact.last_name,
								 contacts_email=bfacontact.email,
								 contacts_phone=bfacontact.phone,
								 contacts_address=bfacontact.address,
								 contacts_city=bfacontact.addr_city,
								 contacts_state=bfacontact.state,
								 contacts_zip=bfacontact.zip,
								 biblestudy_interest=bfacontact.bfa_wantbiblestudy,
								 contacts_books=bfacontact.bfa_orderitems,
								 oms_date_ordered=datetime.datetime.date(bfacontact.bfa_dateordered),
								 customer_id=bfacontact.bfa_customerid)
		new_session.add(newcontact)
		new_session.commit()

		# build mapping
		bfacontact2contact[bfacontact.id] = newcontact.contact_id

		# build bfacontact to user relationship
		newcontactmember = ContactsMembersNew(contact_id=newcontact.contact_id, member_id=user2user[row.user_id])  # which is this? 
		new_session.add(newcontactmember)
		new_session.commit()
	else:
		continue

""" migrate contact comments
	- migrate each comment
	- find via id depending on whether bfa or nonbfa contact
"""

for comment in CommentsOld.query.all():
	if comment.commentable_type == "BfaContact":
		if bfacontact2contact[comment.commentable_id] is not None:
			newcontactcomment = ContactsCommentsNew(contact_id=bfacontact2contact[comment.commentable_id],
													member_id=user2user[comment.user_id],  # which is this?  
													contact_comment=comment.content,
													date_added=comment.created_at)
			new_session.add(newcontactcomment)
			new_session.commit()
		else:
			continue
	elif: comment.commentable_type == "Contact":
		if contact2contact[comment.commentable_id] is not None:
			newcontactcomment = ContactsCommentsNew(contact_id=contact2contact[comment.commentable_id],
													member_id=user2user[comment.user_id],  # which is this?
													contact_comment=comment.content,
													date_added=comment.created_at)
			new_session.add(newcontactcomment)
			new_session.commit()
	else:
		continue





