import asyncio
# from pprint import pprint, pformat
from json import loads
from loguru import logger

from app.api.endpoints.event_recs import event_rec_route

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coroutine = event_rec_route('lofi', 2022, month=8)
    res = loop.run_until_complete(coroutine)
    body = res.body.decode(res.charset)
    logger.debug("result has %d entries" % len(loads(res.body.decode())))
    # logger.debug(pformat(body))
    loop.close()
