from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from backend.models.database import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
