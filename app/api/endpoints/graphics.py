import requests
import os
from tempfile import mkstemp

from fastapi import APIRouter, File, UploadFile, Request
from fastapi.responses import JSONResponse, HTMLResponse
from loguru import logger
from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError

from app.config import Settings

graphics_router = APIRouter()


@graphics_router.post("/resize_picture_upload")
async def resize_picture_upload(picture: UploadFile = File(...), width: int = 500, height: int = 500):
    response = {"status": "failed"}
    pkey_file, pkey_file_name = mkstemp()
    with open(pkey_file, 'w') as pkey_file:
        pkey_file.write(os.environ.get('SSH_PKEY'))

    try:
        logger.debug('Connecting to the remote vm api ...')

        # QUERY PRIVATE API THROUGH SSH TUNNEL
        with SSHTunnelForwarder(
                (Settings.SSH_HOST, 22),
                ssh_username="root",
                ssh_pkey=pkey_file_name,
                remote_bind_address=(Settings.LOCALHOST, Settings.REMOTE_RESIZE_API_BIND_PORT),
                local_bind_address=(Settings.LOCALHOST, Settings.LOCAL_RESIZE_API_BIND_PORT)
        ) as ssh_tunnel:

            url = 'http://' + Settings.LOCALHOST + ':' + str(Settings.LOCAL_RESIZE_API_BIND_PORT) + '/resize_picture_upload'
            querystring = {"width": width, "height": height}
            headers = {
                "accept": "application/json",
            }
            files = {'picture': picture.file.read()}
            response = requests.request("POST", url, files=files, headers=headers, params=querystring)

    except BaseSSHTunnelForwarderError as e:
        raise e
    except Exception as e:
        logger.error('Private API Request Has Failed...')
        raise e
    finally:
        os.unlink(pkey_file_name)

    # return image using fastapi.responses.HTMLResponse
    return JSONResponse(response.json())


@graphics_router.get("/resize_picture_result")
async def resize_picture_result(task_id: int = 1):
    pkey_file, pkey_file_name = mkstemp()
    with open(pkey_file, 'w') as pkey_file:
        pkey_file.write(os.environ.get('SSH_PKEY'))

    try:
        logger.debug('Connecting to the remote vm api ...')

        # QUERY PRIVATE API THROUGH SSH TUNNEL
        with SSHTunnelForwarder(
                (Settings.SSH_HOST, 22),
                ssh_username="root",
                ssh_pkey=pkey_file_name,
                remote_bind_address=(Settings.LOCALHOST, Settings.REMOTE_RESIZE_API_BIND_PORT),
                local_bind_address=(Settings.LOCALHOST, Settings.LOCAL_RESIZE_API_BIND_PORT)
        ) as ssh_tunnel:

            url = 'http://' + Settings.LOCALHOST + ':' + str(Settings.LOCAL_RESIZE_API_BIND_PORT) + '/resize_picture_result'
            querystring = {"task_id": task_id}
            headers = {"accept": "application/json"}
            response = requests.request("GET", url, headers=headers, params=querystring)

    except BaseSSHTunnelForwarderError as e:
        raise e
    except Exception as e:
        logger.error('Private API Request Has Failed...')
        raise e
    finally:
        os.unlink(pkey_file_name)

    content = response.content

    if response.status_code == 200:
        return HTMLResponse(content=content, status_code=200, media_type="image/png")

    # return image using fastapi.responses.HTMLResponse
    return HTMLResponse(content=content, status_code=response.status_code)
