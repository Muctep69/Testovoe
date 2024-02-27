from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1@localhost/test_db"

# Создаем экземпляр движка SQLAlchemy для подключения к базе данных
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
    # Проверяем соединение с базой данных
    engine.connect()
except OperationalError as e:
    print(f"Error connecting to the database: {e}")
    raise

# Создаем экземпляр сессии SQLAlchemy для взаимодействия с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для всех моделей SQLAlchemy
Base = declarative_base()

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
