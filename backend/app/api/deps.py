from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import async_session_factory


async def get_db() -> AsyncIterator[AsyncSession]:
    """Request/task-scoped unit of work: commit on success, roll back on error."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
