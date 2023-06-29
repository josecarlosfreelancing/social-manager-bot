import requests
import os
import json
from os import environ

from app.config import Settings

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = "AAAAAAAAAAAAAAAAAAAAAJnPWQEAAAAAuZGqseMMQz59FsjExAby5K38JeA%3DiwOOsdoviYXtifMpi2aM1p57xZhzx6bCN9WdvtJDpSMesVEUsP"  # os.environ.get("BEARER_TOKEN")

search_url = "https://api.twitter.com/2/spaces"

# Optional params: host_ids,conversation_controls,created_at,creator_id,id,invited_user_ids,is_ticketed,lang,media_key,participants,scheduled_start,speaker_ids,started_at,state,title,updated_at
query_params = {'ids': 'SPACE_ID', 'space.fields': 'title,created_at', 'expansions': 'creator_id'}


def create_headers(bearer_token):
    headers = {
        "Authorization": "Bearer {}".format(bearer_token),
        "User-Agent": "v2SpacesLookupPython"
    }
    return headers


def connect_to_endpoint(url, headers, params):
    response = requests.request("GET", search_url, headers=headers, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def main():
    headers = create_headers(bearer_token)
    json_response = connect_to_endpoint(search_url, headers, query_params)
    print(json.dumps(json_response, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()

# # tests
# if __name__ == '__main__':
#     if environ.get("remote_conf"):
#         Settings.BASE = Settings.PROD_BASE
#     # from app.tests.requests_tests import test, test2, test3, testGPT, testSubjectIntent
