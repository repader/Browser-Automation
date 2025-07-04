from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


DB_DIR = Path(__file__).parent.parent.parent.parent.joinpath('data')
DB_PATH = DB_DIR / 'profiles.sqlite'
DB_URL = f"sqlite+aiosqlite:///{DB_PATH.as_posix()}"

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    data = Column(JSON, default={
        "wallet": None,
        "email": None,
        "proxy": None,
        "twitter": None,
        "discord": None,
    })
    profile_metadata = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    def __getitem__(self, key: str) -> Any:
        if key in self.__table__.columns.keys():
            return getattr(self, key)
        return self.data.get(key)

    def __setitem__(self, key: str, value: Any):
        if key in self.__table__.columns.keys():
            setattr(self, key, value)
        elif key in self.data:
            self.data[key] = value

    def update_fields(self, **kwargs):
        for key, value in kwargs.items():
            self[key] = value
    def update_metadata(self, **kwargs):
        setattr(self, 'profile_metadata', kwargs)

engine = create_async_engine(DB_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


