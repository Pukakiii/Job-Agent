from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.db import engine, init_db
from app.core.logger import configure_logging, get_logger

logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await init_db()
    logger.info("API startup complete.")
    yield
    await engine.dispose()
    logger.info("API shutdown complete.")


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}
