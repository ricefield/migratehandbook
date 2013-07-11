from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

""" migrate.py | a tool for migrating the GTCA handbooks

"""

# creates an engine for the old handbook database
# user `bfa` has all permissions on both old and new handbook databases
oldhb = create_engine('mysql://bfa:gtca@localhost:5432/oldhanbook', echo=False) # set echo to True to debug

# another engine for the new handbook's database
newhb = create_engine('mysql://bfa:gtca@localhost:5432/newhandbook')