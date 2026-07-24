from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, JSON, Text
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("DB")

# creating engine
engine = create_engine(DATABASE_URL.replace("postgres://", "postgresql://", 1))

# creating base
base = declarative_base()


# creating model

class User(base, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    password = Column(String, nullable=False)
    email = Column(String(200), nullable=False, unique=True)
    games = relationship("Game", secondary='user_games', back_populates="users")

    def __repr__(self):
        return f"<User (name ={self.name}) id={self.id} email={self.email}>"


class Game(base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    metacritic = Column(String(100), nullable=False)
    background = Column(String(300), nullable=False)
    release_date = Column(String(100), nullable=False)
    rating = Column(String(100), nullable=False)
    publishers = Column(String(100), nullable=False)
    genre = Column(String(100), nullable=True)
    screenshots = Column(JSON, nullable=False)
    description = Column(Text, nullable=False)
    users = relationship("User", secondary='user_games', back_populates="games")


class UserGames(base):
    __tablename__ = "user_games"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)


#     binding model with engine
# base.metadata.create_all(engine)

# creating session
Session = sessionmaker(bind=engine)
session = Session()
