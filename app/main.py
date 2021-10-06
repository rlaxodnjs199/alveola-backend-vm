from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config


app = FastAPI()

origins = ["http://localhost:3000", "localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to my To Do list"}


@app.get("/info")
async def info():
    return {
        "raw": config.RAW_CT_PATH,
        "deid": config.DEID_CT_PATH,
        "vidaProcessed": config.VIDA_PROCESSED_CT_PATH,
    }
