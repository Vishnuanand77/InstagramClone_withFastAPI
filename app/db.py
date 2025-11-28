"""
This file contains the database configuration and models for the InstagramClone API.
"""

from collections.abc import AsyncGenerator
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from fastapi import Depends

"""
AsyncGenerator: A generator that yields AsyncSession objects.
uuid: A universally unique identifier.
AsyncSession: A session object for asynchronous database operations.

Async methods help FastAPI handle database work without blocking the event loop. While one query processes a db put event, others can process other requests in the background, making the API more responsive and fast.

"""

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Data Models

class Base(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base):
    posts = relationship("Post", back_populates="user")

class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="posts")


engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

"""
Creates the database and tables.
"""
async def create_db_and_tables():
    """
    async with is a context manager. It ensures all the resources are acquired and released by using the await keyword. Here we are awaiting the connection to the database and creating all the tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

"""
A generator that yields AsyncSession objects. We can get a session object from the generator and use it to perform database operations. This allows asynchronouse database operations.

- Every request to the asycn generator will create a new session object and concurrent requests can run in parallel. FastAPI will track each one by building a dependency graph until it finishes and releases the session object.
"""
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)