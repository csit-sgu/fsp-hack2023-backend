from sqlalchemy import MetaData

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from db.models import Base

def init_connection(conn_string):
  engine = create_engine(conn_string, echo=True)
  session = sessionmaker(
    engine, expire_on_commit=False
  )
  
  Base.metadata.create_all(engine)
  
  return engine, session
