import os
from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database URL configuration
DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./DB/sql_app.db")

# For SQLite, we need specific connect_args
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Shloka(Base):
    __tablename__ = "slokas"
    id = Column(Integer, primary_key=True, index=True)
    chapter = Column(Integer, index=True)
    verse = Column(Integer, index=True)
    sanskrit_text = Column(Text)
    transliteration = Column(Text)
    english_meaning = Column(Text)
