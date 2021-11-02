from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.api.v1.scan.endpoints import scan_router
from app.db.pgsql.session import init_db


app = FastAPI(debug=settings.DEBUG)
app.include_router(scan_router)

origins = ["http://localhost:3000", "localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await init_db()
    logger.info("DB session created")


@app.get("/", tags=["root"])
async def root() -> dict:
    return {"message": "Welcome to my app"}
