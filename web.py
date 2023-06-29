from loguru import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.api.api import api_router
from app.general import redis_connection

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://snikpic-ratasorin.vercel.app",
    "https://agency.snikpic.io",
]

app = FastAPI(
    title=Settings.PROJECT_NAME,
)

app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def delete_db_redis():
    redis_connection.close()


@app.on_event("startup")
async def app_startup():
    for key in redis_connection.keys():
        redis_connection.delete(key)
    logger.info("Starting up...")


@app.on_event("shutdown")
async def app_shutdown():
    await delete_db_redis()
    logger.info("Shutting down...")


if __name__ == '__main__':
    import uvicorn
    # uvicorn.run(app, host="127.0.0.1", port=Settings.PORT)
    uvicorn.run("web:app", host="127.0.0.1", port=Settings.PORT)
