from typing import Annotated
from fastapi import (
    Depends,
    FastAPI,
    Request,
    WebSocket,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine
from contextlib import asynccontextmanager

from core.dependencies import DatabaseSettings
from core.models import Base

from posts.router import router as posts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    
    print("Creating database")
    settings = DatabaseSettings()
    engine = create_async_engine(settings.async_database_uri)
    async with engine.begin() as conn:
        print(f"Creating tables {Base.metadata.tables.keys()}")
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()

    yield

# Initialize FastAPI app and templates
app = FastAPI(lifespan=lifespan)

app.include_router(posts_router)