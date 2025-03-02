from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Session
from datetime import datetime
from backend.models.database import Base, get_db

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(100), nullable=False)  
    message = Column(String(500), nullable=False)  
    response = Column(String(5000), nullable=False)  
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chats")

