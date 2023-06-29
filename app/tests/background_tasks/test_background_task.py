from typing import Union
from time import sleep

from fastapi import BackgroundTasks, Depends, FastAPI
from loguru import logger

from app.config import Settings

app = FastAPI()


def write_log(message: str):
    with open("log.txt", mode="a") as log:
        sleep(5)
        log.write(message)
    logger.info(f"write_log finished, message:{message}")


def get_query(background_tasks: BackgroundTasks, q: Union[str, None] = None):
    if q:
        message = f"found query: {q}\n"
    else:
        message = f"not found query: {q}\n"
    background_tasks.add_task(write_log, message)
    logger.info(f"get_query finished, q:{q}")
    return q


@app.post("/send-notification/{email}")
async def send_notification(
    email: str, background_tasks: BackgroundTasks, q: str = Depends(get_query)
):
    message = f"message to {email}\n"
    # background_tasks.add_task(write_log, message)
    logger.info("send_notification finished")
    return {"message": "Message sent"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=Settings.LOCALHOST, port=5050)
