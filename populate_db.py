import csv
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from hello import Flat

engine = create_engine('sqlite:///data.sqlite', echo=True)

Base = declarative_base()