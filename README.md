# SocialManagerBot
=======
## set api keys
make sure to set api keys in `.env` file.
put .pem in the root directory of the project

## running application
setup virtualenv
```commandline
virtualenv venv
```

installing application, run:
```commandline
pip install -r requirements.txt
```



running application using `web.py` or gunicorn.
```commandline
python web.py
```
or with gunicorn.
```commandline
bash scripts/run_gunicorn.sh
```

## environment variables to set up on Heroku
```
GUNICORN_CMD_ARGS (https://docs.gunicorn.org/en/stable/settings.html#settings)
e.g. '--timeout=180 --log-level debug -w 1 -k uvicorn.workers.UvicornWorker'
SSH_PKEY
PG_DB_PW
DAYS_YEAR_API_X_API_KEY
```
For local deployment
```
SERVER_PATH_PORT="localhost:5000"
```

## View logs on Heroku
```commandline
heroku logs --app socialmanagerbot --tail
```