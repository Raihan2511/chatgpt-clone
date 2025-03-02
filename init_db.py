from backend.models.database import Base, engine
from backend.models.user import User
from backend.models.logs import Log
from backend.models.chat_history import ChatHistory
from sqlalchemy.exc import SQLAlchemyError

def initialize_db():
    """Initialize the database and create tables."""
    try:
        print("🔍 Checking tables before creation:", Base.metadata.tables.keys())
        print("🛠 Creating database tables...")
        Base.metadata.create_all(engine)  
        print("✅ Database tables created successfully!")
        print("🔍 Checking tables after creation:", Base.metadata.tables.keys())
    except SQLAlchemyError as e:
        print(f"❌ Error creating database tables: {e}")

if __name__ == '__main__':
    initialize_db()
