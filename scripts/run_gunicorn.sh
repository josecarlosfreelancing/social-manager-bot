#!/usr/bin/env bash
gunicorn -b :5000 --access-logfile logs/access.log --error-logfile logs/error.log -w 3 -k uvicorn.workers.UvicornWorker web:app