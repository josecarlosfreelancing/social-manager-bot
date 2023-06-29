from os import environ, environb
from dotenv import load_dotenv
from urllib.parse import quote_plus as urlquote

load_dotenv()


class Settings:
    PROJECT_NAME = "Snikpic Social Manager API"
    PORT = 5000
    PROD_BASE = "https://socialmanagerbot.herokuapp.com/"
    BASE = f"http://127.0.0.1:{PORT}/"
    DEEPL_URL = "https://api.deepl.com"

    TWITTER_API_KEY = environ.get('TWITTER_API_KEY')
    TWITTER_SECRET = environ.get('TWITTER_SECRET')
    NLP_CLOUD_ID_TOKEN = environ.get('NLP_CLOUD_ID_TOKEN')
    DAYS_YEAR_API_X_API_KEY = environ.get('DAYS_YEAR_API_X_API_KEY')

    SSH_UN = "root"
    SSH_PKEY = environ.get("SSH_PKEY")

    SSH_HOST = "167.235.25.129"
    LOCALHOST = "127.0.0.1"
    REMOTE_BIND_PORT = 5000
    LOCAL_EVENT_REC_BIND_PORT = 5005
    LOCAL_SUBREDDIT_REC_BIND_PORT = 5009
    LOCAL_PAST_EVENTS_REC_BIND_PORT = 5011

    REMOTE_RESIZE_API_BIND_HOST = "127.0.0.1"
    REMOTE_RESIZE_API_BIND_PORT = 5001
    LOCAL_RESIZE_API_BIND_PORT = 5003

    EVENT_EMBEDDING_MODEL = "text-similarity-davinci-001"

    REDDIT_TOKEN = "UAjAVE3_eLmCoTEyPbCzu_Cn-DOC9A"
    REDDIT_CLIENT_ID = "R5gxw7YLEnb11plbJOA8uw"
    REDDIT_USER_AGENT = "Social Auto Agent"

    REPLICATE_MODEL_NAME = "rmokady/clip_prefix_caption"
    REPLICATE_MODEL_VERSION = "9a34a6339872a03f45236f114321fb51fc7aa8269d38ae0ce5334969981e4cd8"

    REDIS_DB = '/tmp/redis.db'
    SERVER_PATH_PORT = environ.get("SERVER_PATH_PORT") or "wss://socialmanagerbot.herokuapp.com:443"
    

settings = Settings()
