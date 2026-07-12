import os

from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv()


POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_PORT_VALUE = int(POSTGRES_PORT) if POSTGRES_PORT else None

DATABASE_ECHO = os.getenv("DATABASE_ECHO", False)
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT_VALUE,
    database=POSTGRES_DB,
)
