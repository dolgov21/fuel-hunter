from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from src.core.config import DATABASE_URL, DATABASE_ECHO


engine = create_engine(DATABASE_URL, echo=DATABASE_ECHO)
session_maker = sessionmaker(engine)

async_engine = create_async_engine(DATABASE_URL, echo=DATABASE_ECHO)
async_session_maker = async_sessionmaker(async_engine)


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )
