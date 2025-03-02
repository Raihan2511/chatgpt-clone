from sqlalchemy.orm import Session
from backend.models.user import User
from backend.models.database import get_db
import hashlib

def hash_password(password: str) -> str:
    """Hash passwords for security."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username: str, password: str):
    """Create a new user in the database."""
    db: Session = next(get_db())
    try:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return None  # Username already exists
        
        hashed_password = hash_password(password)
        new_user = User(username=username, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    finally:
        db.close()

def authenticate_user(username: str, password: str):
    """Check if username and password are correct."""
    db: Session = next(get_db())
    try:
        hashed_password = hash_password(password)
        user = db.query(User).filter(User.username == username, User.password == hashed_password).first()
        return user
    finally:
        db.close()
