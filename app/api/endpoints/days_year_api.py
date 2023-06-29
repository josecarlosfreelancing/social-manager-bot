import requests

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger
import asyncio
import httpx
from calendar import monthrange

from app.config import Settings

__headers = {'X-Api-Key': Settings.DAYS_YEAR_API_X_API_KEY}

days_year_api_router = APIRouter()


DAYSOFTHEYEAR_BASE_URL = 'https://www.daysoftheyear.com/api/v1/'


async def _days_year_api_common(url_ending):
    async with httpx.AsyncClient() as client:

        response = await client.get(DAYSOFTHEYEAR_BASE_URL + url_ending, headers=__headers)

        logger.warning(url_ending)
        # logger.warning(response.text)
        result = response.json()
        json_compatible_item_data = jsonable_encoder(result)
    
    return json_compatible_item_data


async def date_year_month_day(year: int, month: int, day: int = 0):
    """
    Returns events for a specific month.
    Example of usage:
    [https://socialmanagerbot.herokuapp.com/date/2022/01/01](https://socialmanagerbot.herokuapp.com/date/2022/01/01)
    """
    url_ending = f"date/{year:04d}/{month:02d}/{day:02d}"
    if day==0:
        url_ending = url_ending[:-3]
    return await _days_year_api_common(url_ending)


async def date_year_month(year: int, month: int):
    """
    Returns the events for an entire month. Requests are made concurrently
    """
    calls = ( date_year_month_day(year, month, day) for day in range(0, monthrange(year, month)[1]))

    monthly_events = await asyncio.gather(*calls)

    return monthly_events


@days_year_api_router.get("/today")
async def today_route():
    """
    Returns events for today’s date.
    Example of usage:
    [https://socialmanagerbot.herokuapp.com/today](https://socialmanagerbot.herokuapp.com/today)
    """
    url_ending = "today"
    result = await _days_year_api_common(url_ending)
    return JSONResponse(content=result)


@days_year_api_router.get("/date/{year}/{month}/{day}")
async def date_year_month_day_route(year: int, month: int, day: int):
    """
    Returns events for a specific month.
    Example of usage:
    [https://socialmanagerbot.herokuapp.com/date/2022/01/01](https://socialmanagerbot.herokuapp.com/date/2022/01/01)
    """
    result = await date_year_month_day(year, month, day)
    return JSONResponse(content=result)


@days_year_api_router.get("/date/{year}/{month}")
async def date_year_month_route(year: int, month: int):
    """
    Returns events for a specific date (day).
    Example of usage:
    [https://socialmanagerbot.herokuapp.com/date/2022/01](https://socialmanagerbot.herokuapp.com/date/2022/01)
    """
    result = await date_year_month_day(year, month)
    return JSONResponse(content=result)
