import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.api.dependencies import setup_dependencies
from app.api.routes import router
from app.core.config import settings
from app.core.db import get_async_engine, get_async_sessionmaker
from app.core.exceptions import NotFoundError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_async_engine(settings.database_url)
    sessionmaker = get_async_sessionmaker(engine)

    await setup_dependencies(app=app, sessionmaker=sessionmaker)

    yield

    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="Helpdesk API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"detail": exc.detail})

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
