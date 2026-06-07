from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

engine = create_engine(
    url=settings.DB_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
)

session_factory = sessionmaker(engine)
