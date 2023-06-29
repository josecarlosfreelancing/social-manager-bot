from fastapi import APIRouter

from app.api.endpoints.social_manager_bot import social_manager_router
from app.api.endpoints.instacapions import instacaptions_router
from app.api.endpoints.days_year_api import days_year_api_router
from app.api.endpoints.event_recs import event_recs_router
from app.api.endpoints.past_events_recs import past_events_recs_router
from app.api.endpoints.subreddit_rec import subreddit_recs_router
from app.api.endpoints.tiktok import tiktok_router
from app.api.endpoints.graphics import graphics_router
from app.api.endpoints.prompts import prompts_router
from app.api.endpoints.concepts import concepts_router
from app.views.websockets_view import websockets_view_router

api_router = APIRouter()
api_router.include_router(social_manager_router, tags=["core api"])
api_router.include_router(instacaptions_router, tags=["instacaptions"])
api_router.include_router(days_year_api_router, tags=["days_year_api"])
api_router.include_router(event_recs_router, tags=["event_recs_api"])
api_router.include_router(past_events_recs_router, tags=["past_events_recs_api"])
api_router.include_router(subreddit_recs_router, tags=["reddit_api"])
api_router.include_router(tiktok_router, tags=["tiktok_api"])
api_router.include_router(graphics_router, tags=["graphics_api"])
api_router.include_router(prompts_router, tags=["prompts_api"])
api_router.include_router(concepts_router, tags=["concepts_api"])
api_router.include_router(websockets_view_router, tags=["websockets_view"])
