import os

try:
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from sqlalchemy.orm import DeclarativeBase
except ImportError:
    create_async_engine = None
    async_sessionmaker = None
    AsyncSession = None
    DeclarativeBase = object
    engine = None
    async_session = None
    Base = None
    DB_ENABLED = False

    async def init_db():
        return
else:
    DB_ENABLED = True
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL не задано в .env")

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession
    )

    class Base(DeclarativeBase):
        pass

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
