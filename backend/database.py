import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# On pourra ajuster l'URL avec un fichier .env plus tard pour la vraie BDD Docker PostgreSQL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/marketplace_db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
