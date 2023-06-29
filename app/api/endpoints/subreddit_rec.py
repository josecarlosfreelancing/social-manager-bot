import requests
import openai
from loguru import logger

from fastapi import APIRouter
from typing import Any, Optional
import asyncio

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
import json
# from app.schemas import SubredditRecsSchema, SubredditTopSchema
from app.config import Settings

from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError
import os
from tempfile import mkstemp

import asyncpraw

subreddit_recs_router = APIRouter()


###### Setup vm connection to get the event-scores
# 1.QUERY PRIVATE API THROUGH SSH TUNNEL
def get_subreddit_recs(description, n_recs):

    pkey_file, pkey_file_name = mkstemp()
    with open(pkey_file, 'w') as pkey_file:
        pkey_file.write(os.environ.get('SSH_PKEY'))

    try:
        logger.debug('Connecting to the private vm api ...')

        with SSHTunnelForwarder(
                (Settings.SSH_HOST, 22),
                ssh_username="root",
                ssh_pkey=pkey_file_name,
                remote_bind_address=(Settings.LOCALHOST, Settings.REMOTE_BIND_PORT),
                local_bind_address=(Settings.LOCALHOST, Settings.LOCAL_SUBREDDIT_REC_BIND_PORT)
        ) as ssh_tunnel:
            logger.debug('connected')

            params = json.dumps({'description':description, 'n_recs':n_recs})
            response = requests.post('http://'+Settings.LOCALHOST+':'+str(Settings.LOCAL_SUBREDDIT_REC_BIND_PORT)+'/get_subreddit_rec', data=params)

            os.unlink(pkey_file_name)

    except BaseSSHTunnelForwarderError as e:
        raise e
    except Exception as e:
        logger.error('Private API Request Has Failed...')
        raise e

    return json.loads(response.text)

async def get_subreddit_posts(sub_id, n_posts, ranking_method, top_timeframe, ignore_404_assets):
    reddit = asyncpraw.Reddit(
        client_id=Settings.REDDIT_CLIENT_ID,
        client_secret=Settings.REDDIT_TOKEN,
        user_agent=Settings.REDDIT_USER_AGENT,
    )

    sub = await reddit.subreddit(sub_id)

    # :set limit higher than target to filter out any posts with 404_assets 
    if ranking_method=='top':
        posts_gen = sub.top(top_timeframe, limit=2*n_posts)
    else:
        posts_gen = getattr(sub, ranking_method)(limit=2*n_posts)
    
    posts = []

    async for post in posts_gen:

        tmp_post = {}

        #{url, title, body, assets, external links}
        tmp_post = {}
        tmp_post['subreddit'] = post.subreddit.display_name
        tmp_post['url'] = 'https://www.reddit.com'+post.permalink
        tmp_post['title'] = post.title
        tmp_post['body'] = post.selftext

        # check if the post content still exists:
        response = requests.get(post.url)

        if response.status_code==404:
              
            if ignore_404_assets:
                tmp_post['error_flags'] = ["Some contents may not be reachable."]
            else:
                # skip post
                continue
        # collect assets
        tmp_post['assets'] = {}
        if post.media:
            if "reddit_video" in post.media:
                tmp_post['assets']['reddit_video'] = post.media['reddit_video']['fallback_url']
            # collect assets in embedded content: yt video, twitter etc.
            if "oembed" in post.media:
                if "url" in post.media['oembed']:
                    tmp_post['assets']['embedded_content'] = post.media['oembed']['url']
                    # handle yt vid
                elif "html" in post.media['oembed']:
                    tmp_post['assets']['embedded_content'] = post.media['oembed']['html'].split('src="')[1].split('" ')[0]

        if post.thumbnail not in ['', 'self', 'default']:
            tmp_post['assets']['thumbnail'] = post.thumbnail

        if post.url != tmp_post['url']:
            # handle image posts; url points back to reddit
            if '.redd.' in post.url:
                tmp_post['assets']['image'] = post.url
            elif '.reddit.com' not in post.url and 'youtube.com' not in post.url:
                tmp_post['external_links'] = post.url

        posts.append(tmp_post)

        # check if posts are collected:
        if len(posts)==n_posts:
            # exit loop
            break

    await reddit.close()
    return posts

@subreddit_recs_router.post('/subreddit_rec/')
async def subreddit_rec(description:str, num_recs:int = 5):
    '''
    Return a list of relevant subreddits, given a description text.
    '''
    subreddits = []

    response = get_subreddit_recs(description, num_recs)

    return JSONResponse(response)



@subreddit_recs_router.post('/subreddit_post_list/')
async def subreddit_post_list(subreddit_ids:list = ['yoga', 'python'], 
                            n_posts: int = 3, 
                            ranking_method: str = 'hot', 
                            top_timeframe: Optional[str] = 'hour',
                            ignore_404_assets: Optional[bool] = True ):
    '''
    Return a list of posts extracted from a list of subreddits.
    - subreddit_ids: list = ['yoga', 'python']
    - n_posts: int = 3
    - ranking_method: str = 'hot' # hot, new, top, rising
    - top_timeframe: Optional[str] = 'hour' # hour, day, week, month, year, all
    - ignore_404_assets: if non-zero integer, avoid returning posts with non-reachable post-assets.
    '''

    # # create async calls for asyncpraw
    calls = (get_subreddit_posts(sub_id, n_posts, ranking_method, top_timeframe, ignore_404_assets) for sub_id in subreddit_ids)
    
    posts = await asyncio.gather(*calls)


    

    return JSONResponse(posts)










