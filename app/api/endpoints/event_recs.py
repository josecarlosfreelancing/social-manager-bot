import requests
from json import loads
from tempfile import mkstemp

import openai
import numpy as np
from calendar import monthrange
from loguru import logger

from fastapi import APIRouter
from typing import Any, Optional
import asyncio
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.config import Settings
from app.api.endpoints.days_year_api import date_year_month_day, date_year_month

import json
import os
from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError

event_recs_router = APIRouter()


###### Setup vm connection to get the event-scores
# 1.QUERY PRIVATE API THROUGH SSH TUNNEL
def get_event_scores(desc, excerpts):
    pkey_file, pkey_file_name = mkstemp()
    with open(pkey_file, 'w') as pkey_file:
        pkey_file.write(os.environ.get('SSH_PKEY'))

    try:
        logger.debug('Connecting to the remote vm api ...')

        with SSHTunnelForwarder(
                (Settings.SSH_HOST, 22),
                ssh_username="root",
                ssh_pkey=pkey_file_name,
                remote_bind_address=(Settings.LOCALHOST, Settings.REMOTE_BIND_PORT),
                local_bind_address=(Settings.LOCALHOST, Settings.LOCAL_EVENT_REC_BIND_PORT)
        ) as ssh_tunnel:

            # request similarity scores
            params = json.dumps({'desc': desc, 'excerpts': excerpts})
            response = requests.post(
                'http://' + Settings.LOCALHOST + ':' + str(Settings.LOCAL_EVENT_REC_BIND_PORT) + '/get_event_scores',
                data=params)

            os.unlink(pkey_file_name)

    except BaseSSHTunnelForwarderError as e:
        raise e
    except Exception as e:
        logger.error('Private API Request Has Failed...')
        raise e

    return json.loads(response.text)


def parse_events(events, year, month, day):
    date = "{}/{}/{}".format(year, month, day)

    if day == 0:
        date = "{}/{}".format(year, month)

    return [
        {'name': event['name'],
         'excerpt': event['excerpt'].strip(),
         'date': date,
         'url': event['url'],
         'score': 0}
        for event in events
    ]


@event_recs_router.post('/event_rec/')
async def event_rec_route(
        desc: str = ("restaurant that blends Belgian and asiatic flavours in a vintage bistro setting "
                     "with draught beer and fine wines"),
        year: int = 2022,
        month: int = 4,
        day: Optional[int] = None):
    """
    Return a list of events for a given description.

    - If day == 0 : returns scored monthly events only
    - If day is None, returns scored monthly and daily events
    """
    events = []

    logger.debug("started getting events")

    # check if day is provided
    if day is not None:
        # get list of events for the specific day
        events = await date_year_month_day(year, month, day)
        events = events['data']
        events = parse_events(events, year, month, day)
    else:
        # get list of events for the specific month
        # in the list-of-lists format
        monthly_events = await date_year_month(year, month)

        for i in range(len(monthly_events)):
            events += parse_events(monthly_events[i]['data'], year, month, i)

    logger.debug("result has %d events entries" % len(events))

    # Get the events similarity scores from the Private Api
    scores = get_event_scores(desc, [event['excerpt'] for event in events])

    events_to_return = []
    for index in np.argsort(-np.array(scores)):
        # update score
        events[index]['score'] = scores[index]
        events_to_return.append(events[index])

    logger.debug("result has %d event_rec entries" % len(events_to_return))

    return JSONResponse(events_to_return)
