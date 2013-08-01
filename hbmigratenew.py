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

class ContactsOld(Entity):
	""" oldhandbook/contacts """
	using_options(metadata=old_metadata, session=old_session, tablename="contacts", autoload=True)

class CommentsOld(Entity):
	""" oldhandbook/comments """
	using_options(metadata=old_metadata, session=old_session, tablename="comments", autoload=True)

# new
class ContactsNew(Entity):
	""" newhandbook/bf_contacts """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_contacts", autoload=True)

class ContactsCommentsNew(Entity):
	""" newhandbook/bf_contacts_comments """
	using_options(metadata=new_metadata, session=new_session, tablename="bf_contacts_comments", autoload=True)


""" migration """

for city, team in cities.iteritems:

	logging.info("### migrating city id #" + city + "###")

	logging.info("### migrating contacts ###")

	contact2contact = {} # mapping of old (non-bfa) contacts to new contacts
	bfacontact2contact = {} # mapping of old bfa contacts to new contacts

	# old contacts -- only import those within the past year
	for contact in ContactsOld.query.filter_by(city_id=city):
			# create new contact
			newcontact = ContactsNew(team_id=team,
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

	""" migrate contact comments """

	logging.info("### migrating contact comments ###")

	for comment in CommentsOld.query.all():
		if comment.commentable_type == "Contact":
			try:
				if contact2contact[comment.commentable_id] is not None:
					newcontactcomment = ContactsCommentsNew(contact_id=contact2contact[comment.commentable_id],
															member_id=user2member[comment.user_id],
															contact_comment=comment.content,
															date_added=comment.created_at)
					new_session.add(newcontactcomment)
					new_session.commit()
			except KeyError:
				logging.error("no contact with id#"+str(comment.commentable_id)+" (likely not imported). not migrating comment")
		else:
			continue
