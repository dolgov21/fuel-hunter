import os

from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv()


POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_HOST_PORT = int(os.getenv("POSTGRES_HOST_PORT", "5432"))

DATABASE_ECHO = os.getenv("DATABASE_ECHO", False)
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_HOST_PORT,
    database=POSTGRES_DB,
)

RABBITMQ_DEFAULT_USER = os.getenv("RABBITMQ_DEFAULT_USER")
RABBITMQ_DEFAULT_PASS = os.getenv("RABBITMQ_DEFAULT_PASS")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_HOST_PORT = os.getenv("RABBITMQ_HOST_PORT")

CELERY_BROKER_URL = f"amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}@{RABBITMQ_HOST}:{RABBITMQ_HOST_PORT}"