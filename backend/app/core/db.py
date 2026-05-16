from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


def get_async_engine(postgres_dsn: str, pool_size: int = 50) -> AsyncEngine:
    return create_async_engine(
        url=postgres_dsn,
        echo=False,
        # Validate connections before handing them out of the pool.
        # Without this, idle connections killed by Postgres (timeouts, restarts) are
        # returned from the pool and the first query fails with "connection is closed".
        pool_pre_ping=True,
        # Recycle connections every 30 min as a safety net against long-lived idle conns.
        pool_recycle=1800,
        pool_size=pool_size,
        max_overflow=0,
    )


def get_async_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
