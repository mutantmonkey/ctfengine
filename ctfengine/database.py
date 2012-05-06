from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from ctfengine import app

engine = create_engine(app.config['DATABASE'], convert_unicode=True)
conn = scoped_session(sessionmaker(autocommit=False, autoflush=False,
    bind=engine))

Base = declarative_base()
Base.query = conn.query_property()


def init_db():
    import ctfengine.models
    Base.metadata.create_all(bind=engine)
