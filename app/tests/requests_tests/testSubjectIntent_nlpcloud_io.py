import nlpcloud
import requests
from json import loads
from os import environ

from app.config import Settings

from loguru import logger

from app.core.ai import NLP_CLOUD_LABELS

logger.info(f'---{__name__}---')

raise NotImplemented

# REQUEST FORMAT
NLP_CLOUD_ID_TOKEN = environ['NLP_CLOUD_ID_TOKEN']

#text3 = "Keep the one for saturday. A feedback, real quick. 1 Talk more about our values 2 Our hashtag is #we are mad. I sent examples 2 weeks ago, let's take the last one with snoop dog. You can have a pic with bunch of people having a party, eating crackers, drinking wine. Happy people, happy moments. Then, the day after, one of them, laying on the couch, huge hangover, in pyjama's with again a bag of crackers, line 'Nigel crackerss, cure the hangover', stuff like that."
#text2 = "Bonjour ! J'aimerais que vous ajoutiez  mon associé Thomas dans le groupe svp. +32468085206"
#text4 = "j'aimerais avoir mes factures"
text = "Bonjour, j’ai réglé le problème sur mon site, il est opérationnel maintenant. Par contre je voudrais arrêter avec la pub Google. J’ai mis une pub sur Facebook la semaine passée et ça tourne bien je préfère donc assigner mon budget à cet outil.  Du coup je souhaite arrêter avec le service Google Ads management aussi. On est à la moitié de la période qui est déjà payée et donc je souhaite plus être facturée cet service le 15/12. Est-ce que c’est ok de vous informer par ici ou dois-je communiquer cela par e-mail ?"
text_intent_answer = {'Intent': 'changeRequest'}

headers = {"Content-Type": "application/json"}
payload = {'text': text}

response = requests.post(Settings.BASE + "intentAnalysis", json=payload, headers=headers)
# print('/n /n Test')
intent_response = loads(response.json())
assert intent_response == text_intent_answer, f"{intent_response}, {text_intent_answer}"

client = nlpcloud.Client("xlm-roberta-large-xnli", Settings.NLP_CLOUD_ID_TOKEN)
classification_result = client.classification("""John Doe is a Go Developer at Google. 
  He has been working there for 10 years and has been 
  awarded employee of the year.""", NLP_CLOUD_LABELS)

labels = classification_result['labels']
intent_result = {'Intent': labels[0]}
logger.info(intent_result)
