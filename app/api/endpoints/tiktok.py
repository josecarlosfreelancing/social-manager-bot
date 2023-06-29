from fastapi import APIRouter

from app.core.ai import getHook
from app.schemas import InstacaptionSchema

tiktok_router = APIRouter()


@tiktok_router.post('/tiktok_video')
async def tiktok_video(text: InstacaptionSchema):
    # Based on instagram caption return a tiktok video
    # The content is same with ai.py I didn't remove it shall we?
    result = getHook(text.texts)

    return result