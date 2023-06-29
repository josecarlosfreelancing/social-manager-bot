import requests
from json import loads
from tempfile import mkstemp

import openai
import numpy as np
from calendar import monthrange
from loguru import logger

from fastapi import APIRouter, Query
from typing import Any, Optional, List, Union
import asyncio
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.config import Settings

import json
import os
from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError

past_events_recs_router = APIRouter()


###### Setup vm connection to get the event-scores
# 1.QUERY PRIVATE API THROUGH SSH TUNNEL
def get_past_events(event_types: List[str],
                    month: int,
                    description: str,
                    sort: bool,
                    top_n: int):
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
                local_bind_address=(Settings.LOCALHOST, Settings.LOCAL_PAST_EVENTS_REC_BIND_PORT)
        ) as ssh_tunnel:

            # request similarity scores
            params = json.dumps({"types": event_types, 
                                "month": month,
                                "description": description,
                                "sort": sort,
                                "top_n": top_n
                                })
            response = requests.post(
                'http://' + Settings.LOCALHOST + ':' + str(Settings.LOCAL_PAST_EVENTS_REC_BIND_PORT) + '/get_events',
                data=params)

            os.unlink(pkey_file_name)

    except BaseSSHTunnelForwarderError as e:
        raise e
    except Exception as e:
        logger.error('Private API Request Has Failed...')
        raise e

    return json.loads(response.text)

@past_events_recs_router.post('/get_past_events/')
async def past_events_rec_route(event_types: Union[List[str], None] = Query(default=['events']), 
                                month: int = 1, 
                                description: str = ("restaurant that blends Belgian and asiatic flavours in a vintage bistro setting with draught beer and fine wines"), 
                                sort: bool = True, 
                                top_n: int = 50):

    """
    Return a list of historical events for a given description and a month .
        event_types - can consist of a selection of the elements in the list ['events', 'deaths', 'births']
        month: month in integer format, 
        description: str = ("restaurant that blends Belgian and asiatic flavours in a vintage bistro setting with draught beer and fine wines"), 
        sort: If sort is off, a list of events will be returned regardless of their similarity with the description, 
        top_n: Number of results to return for each event type specified in the list.        
    """

    events_to_return = get_past_events(event_types, month, description, sort, top_n)



    return JSONResponse(events_to_return)



