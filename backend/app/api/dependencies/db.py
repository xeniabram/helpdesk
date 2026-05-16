from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.dependencies.stubs import get_sessionmaker

SessionmakerDep = Annotated[async_sessionmaker[AsyncSession], Depends(get_sessionmaker)]


async def get_session(sessionmaker: SessionmakerDep) -> AsyncGenerator[AsyncSession]:
    async with sessionmaker() as session, session.begin():
        yield session
