from sqlalchemy import engine, MetaData

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

def init_connection(conn_string):
  engine = create_async_engine(conn_string)
  async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
  )
  
  MetaData(engine).create_all()
  
  return engine, async_session