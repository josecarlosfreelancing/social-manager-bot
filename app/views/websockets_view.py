from fastapi import APIRouter
from loguru import logger
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from app.config import Settings


websockets_view_router = APIRouter()

templates = Jinja2Templates("app/templates")


@websockets_view_router.get("/clip_prefix_caption_ws_view")
async def clip_prefix_caption_ws_view(request: Request):
    context = {'request': request, 'server_path_port': Settings.SERVER_PATH_PORT}
    return templates.TemplateResponse("clip_prefix_caption_ws.html", context)


# @websockets_view_router.websocket("/get_post_ideas_v2_ws_view")
# async def get_post_ideas_v2_ws_view(request: Request):
#     context = {'request': request, 'server_path_port': Settings.SERVER_PATH_PORT}
#     return templates.TemplateResponse("get_post_ideas_v2.html", context)
