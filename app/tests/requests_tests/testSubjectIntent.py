import requests

from app.config import Settings

from loguru import logger

logger.info(f'---{__name__}---')

# REQUEST FORMAT


#text3 = "Keep the one for saturday. A feedback, real quick. 1 Talk more about our values 2 Our hashtag is #we are mad. I sent examples 2 weeks ago, let's take the last one with snoop dog. You can have a pic with bunch of people having a party, eating crackers, drinking wine. Happy people, happy moments. Then, the day after, one of them, laying on the couch, huge hangover, in pyjama's with again a bag of crackers, line 'Nigel crackerss, cure the hangover', stuff like that."
#text2 = "Bonjour ! J'aimerais que vous ajoutiez  mon associé Thomas dans le groupe svp. +32468085206"
#text4 = "j'aimerais avoir mes factures"
text = "Bonjour, j’ai réglé le problème sur mon site, il est opérationnel maintenant. Par contre je voudrais arrêter avec la pub Google. J’ai mis une pub sur Facebook la semaine passée et ça tourne bien je préfère donc assigner mon budget à cet outil.  Du coup je souhaite arrêter avec le service Google Ads management aussi. On est à la moitié de la période qui est déjà payée et donc je souhaite plus être facturée cet service le 15/12. Est-ce que c’est ok de vous informer par ici ou dois-je communiquer cela par e-mail ?"

headers = {"Content-Type": "application/json"}
payload = {'text': text}

response2 = requests.post(Settings.BASE + "subjectEntityAnalysis", json=payload, headers=headers)
logger.info(response2.json())
