from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.dependencies.stubs import (
    get_sessionmaker,
)


async def setup_dependencies(
    app: FastAPI,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    app.dependency_overrides[get_sessionmaker] = lambda: sessionmaker
