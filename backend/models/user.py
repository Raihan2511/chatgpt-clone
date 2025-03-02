from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.models.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    chats = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
