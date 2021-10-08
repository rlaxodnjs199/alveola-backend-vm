from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.ctscan.endpoints import CTscan_router

app = FastAPI()
app.include_router(CTscan_router)

origins = ["http://localhost:3000", "localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
async def root() -> dict:
    return {"message": "Welcome to my app"}
