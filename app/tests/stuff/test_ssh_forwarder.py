import sshtunnel
from sshtunnel import SSHTunnelForwarder
from tempfile import mkstemp
from os import environ

import logging
from loguru import logger

from app.config import Settings

# sshtunnel.SSH_TIMEOUT = 5.0
# sshtunnel.TUNNEL_TIMEOUT = 5.0


from os import abort

LOCAL_PK_PATH = "/home/ray/Projects1/ssh_socialmanagerbot/ssh_socialmanagerbot"
# input here the key file path for test
with open(LOCAL_PK_PATH) as f:
    environ['SSH_PKEY'] = f.read()

from app.api.endpoints import event_recs


pkey_file, pkey_file_name = mkstemp()
pkey_file = open(pkey_file, 'w')
pkey_file.write(environ.get('SSH_PKEY'))
pkey_file.close()


with open(LOCAL_PK_PATH) as f, open(pkey_file_name) as pkey_file:
    sf = f.read()
    spk = str(pkey_file.read())
    print(sf == spk, len(sf), len(spk))


logger.warning('begin w')
logger.info('begin i')


with sshtunnel.SSHTunnelForwarder(
        (Settings.SSH_HOST, 22),
        ssh_username=Settings.SSH_UN,
        ssh_pkey=pkey_file_name,
        remote_bind_address=(Settings.DB_HOST, 5432),
        logger=sshtunnel.create_logger(loglevel=logging.DEBUG)
) as tunnel:
    logger.warning('connected')
