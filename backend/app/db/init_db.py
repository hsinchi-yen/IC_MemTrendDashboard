from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.base import Base

# Import the package so all ORM modules register their tables on Base.metadata.
import app.models  # noqa: F401


async def init_models(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
