import requests
import json

from app.config import Settings

from loguru import logger

logger.info(f'---{__name__}---')


# REQUEST FORMMAT

# Initialisation needs 10 items of 'Concept' / 'Caption' to be efficiently
# Initialisation needs to be a JSON string (e.g., json.dumps in python , json.stringify in nodeJS)
# postRequest is a string of post concept (e.g., Promoting our new smartphone )
# postLanguage is a string of 2 character with language (e.g., 'EN' , 'FR', etc.)

# payload = {
#
#   'Initialisation' : json.dumps([{'Concept' : 'XX' , 'Caption' : 'XX'} , {'Concept' : 'XX' , 'Caption' : 'XX'}]) ,
#   'postRequest':"XX" ,
#   'postLanguage': "XX"
#
#   }

InitialisationDic = [
    {
        'Concept': "Information on Vitamins",
        'Caption': "I love these vitamins"
    },
    {
        'Concept': "Promotion for the summer",
        'Caption': "Huge Discount in summer"
    }
]

headers = {"Content-Type": "application/json"}

postRequest = "Information sur la vitamine C"
postLanguage = "FR"
postCategory = 'Meme'
payload = {'Initialisation': InitialisationDic, 'postRequest': postRequest, 'postLanguage': postLanguage,
           'postCategory': postCategory}

response = requests.post(Settings.BASE + "caption", json=payload, headers=headers)
# print('/n /n Test')
response_json = response.json()
logger.info(str(response_json))
