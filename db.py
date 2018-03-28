from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///ads.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Ad(Base):
    __tablename__ = "ads"
    id = Column(Integer, primary_key = True)
    title = Column(String)
    price = Column(String)
    published = Column(Boolean)
    ownerId = Column(Integer)
    ownerUsername = Column(String)
    ownerContact = Column(String)
    deleted = Column(Boolean)
    
    def __init__(self, title=None, price=None, published=None, ownerId=None, ownerUsername=None,ownerContact=None, deleted=False):
        self.title = title
        self.price = price
        self.published = published
        self.ownerId = ownerId
        self.ownerUsername = ownerUsername
        self.ownerContact = ownerContact
        self.deleted = deleted
    
    def __str__(self):
        return "<Ad('%s','%s')>" % (self.title, self.price)


Base.metadata.create_all(bind=engine)
