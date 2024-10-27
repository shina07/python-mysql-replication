import json
from functools import wraps

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from common.setting import db_config

DB_URL = (
    f"mysql+asyncmy://"
    f"{db_config.DB_USERNAME}:"
    f"{db_config.DB_PASSWORD}@"
    f"{db_config.DB_HOST}:"
    f"{db_config.DB_PORT}/"
    f"{db_config.DB_NAME}"
)

_engine: AsyncEngine = create_async_engine(
    url=DB_URL,
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    json_serializer=lambda x: json.dumps(x, ensure_ascii=False, indent=2)
)
async_session: async_sessionmaker = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=_engine,
    class_=AsyncSession,
    future=True
)


class AsyncSessionContext:
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = async_session()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        self.session = None


def transactional(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if "session" in kwargs:
            return await func(*args, **kwargs)

        else:
            async with AsyncSessionContext() as session:
                kwargs["session"] = session

                try:
                    result = await func(*args, **kwargs)
                    await session.commit()

                except Exception as e:
                    await session.rollback()
                    raise e

            return result

    return wrapper
