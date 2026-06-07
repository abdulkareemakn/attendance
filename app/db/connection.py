import os
from app.settings import settings

from dotenv import load_dotenv
from sqlmodel import create_engine, Session

load_dotenv()

engine = create_engine(settings.database_url)


def get_db():
    with Session(engine) as session:
        yield session
