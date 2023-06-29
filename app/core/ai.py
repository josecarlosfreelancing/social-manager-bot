import re
from datetime import datetime, date
from io import BytesIO
from typing import Dict, List, Optional

import nlpcloud
import numpy as np
import openai
import replicate
import requests
from fastapi import UploadFile, File
from loguru import logger

from app.api.endpoints.days_year_api import date_year_month
from app.api.endpoints.event_recs import get_event_scores
from app.api.endpoints.past_events_recs import get_past_events
from app.core.ai_utils import get_open_ai_completion, AIProcessingException
from app.core.ai_concepts import getconcept_information, getconcept_promotion, getconcept_inspiration, getconcept_quotes
from scripts.exp_decorator import retry
from app.config import Settings
from app.schemas import PostIdeasCategory

UNKNOWN_AUTHOR = 'Unknown'

DAVINCI_INSTRUCT_BETA = "davinci-instruct-beta"

NLP_CLOUD_LABELS = [
    "make Appointment", "new Request", "change Request", "give Info", "get Info", "give Feedback", "get Help",
    "no Intent"]

replicate_model = replicate.models.get(Settings.REPLICATE_MODEL_NAME)
replicate_version = replicate_model.versions.get(Settings.REPLICATE_MODEL_VERSION)


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getCaption(inputText, InitialisationDic):
    start_sequence = "\nCaption:"
    restart_sequence = "\n###\nConcept:"
    session_prompt_intro = "Given a Concept, generate a Caption\n\nConcept:"
    session_prompt_initial = ""
    session_prompt_initial += f'{session_prompt_intro}'
    for i in range(len(InitialisationDic)):
        session_prompt_initial += f"{InitialisationDic[i]['Concept']}{start_sequence}{InitialisationDic[i]['Caption']}{restart_sequence}"
    prompt_text = f'{session_prompt_initial}{inputText}'

    response = get_open_ai_completion().create(
        engine="text-davinci-003",
        prompt=prompt_text,
        temperature=0.75,
        max_tokens=400,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###"]
    )
    Caption = response['choices'][0]['text']

    return Caption


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getDesign_Inspiration(inputText):
    start_sequence = "\nImage description:"
    restart_sequence = "\n###\nConcept:"
    session_prompt_initial = "Given a Concept, generate an image description and text to appear\n\nConcept: Unexpected summer destinations to go on vacation\nImage description: Picture of a women shopping in the Grand Bazaar in Instabul\nText to appear: /\n###\nConcept: Activities to do with the family\nImage description: Picture of a family having fun at an amusement park\nText to appear: /\n###\nConcept: Sunlight at home\nImage description: Picture of veranda flooded with sunlight\nText to appear: /\n###\nConcept: Start of the summer\nImage description: Picture of an infinity pool in a summer field\nText to appear: /\n###\nConcept: Spring home design\nImage description: Picture of a flower vase with Pansies and Violas on a nightstand next to a bed\nText to appear: /\n###\nConcept: Christmas eve dinner\nImage description: Picture of a happy large family at  dinner table with a big turkey and a christmas tree in the background\nText to appear: /\n###\nConcept: Spring break party\nImage description: Picture of a beach spring break party with many students jumping around and drinking\nText to appear: /  \n###\nConcept: Bathroom\nImage description: Picture of a nice designer bathroom\nText to appear: /\n###\nConcept: Back to school\nImage description: Picture of students in an classroom raising their hands\nText to appear: /\n###\nConcept: Valentine's day\nImage description: Picture of two candy- hearts and a lot of kisses\nText to appear: /"
    prompt_text = f'{restart_sequence}: {inputText}{start_sequence}'
    response = get_open_ai_completion().create(
        engine="davinci-instruct-beta",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.9,
        max_tokens=300,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1,
        stop=["###"]
    )
    Output = response['choices'][0]['text']
    Design_prompt = f'Image description:{Output}'

    return Design_prompt


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getDesign_Information(inputText):
    start_sequence = "\nImage description:"
    restart_sequence = "\n###\nConcept:"
    session_prompt_initial = "Given a Concept, generate an image description and text to appear\n\nConcept: Zinc health benefits\nImage description: Picture of a women in front of a plate of oysters grinning\nText to appear: Benefits of Zinc\n###\nConcept: essential oils usage\nImage description: Shots of multiple essential oil bottles on a shelf\nText to appear: Uses of essential oils\n###\nConcept: Omega-3\nImage description: Picture of multiple products with Omega-3 in them (e.g., salmon, avocado, eggs) on a table\nText to appear: /\n###\nConcept: foot care\nImage description: Picture of someone's feet playing in the water\nText to appear: /\n###\nConcept: natural solutions to mosquitoes\nImage description: Picture of a toddler itching and scratching a mosquitoe bite\nText to appear: /\n###\nConcept: hair loss prevention\nImage description: Picture of a concerned women brushing her hairs and looking at the it through the mirror\nText to appear: /\n###\nConcept: high grass season, allergies and hay fever\nImage description: Picture of someone sneezing into a tissue\nText to appear: Seasonal allergies\n ###\nConcept: natural skin care\nImage description: Picture of a woman rubbing half a lemon on her face\nText to appear: /\n###\nConcept: low back pain\nImage description: Picture of a man holding his lower back in pain\nText to appear: Preventing lower back pain\n###\nConcept: primitive reflex in babies\nImage description: Image of a baby's sucking on his bottle\nText to appear: /\n###\nConcept: boiler maintenance\nImage description: Text on brand predefined template\nText to appear: Boiler maintenance - How to properly do it ?\n###\nConcept: 3 things to do before selling your house\nImage description: Text on brand predefined template\nText to appear: 3 things to do before selling your house\n###\nConcept: Tips and tricks on how to eat healthier\nImage description: Women eating salmon on whole wheat bread\nText to appear: /\n###\nConcept: the benefit of chia seeds in winter\nImage description: Text on brand predefined template\nText to appear: Why chia seeds are winter's superfood ?\n###\nConcept: how to read a tire band\nImage description: Picture of a tire\nText to appear: /\n###\nConcept: top 3 things to stimulate your baby\nImage description: Picture of smiling baby making eye contact with mom\nText to appear:  Top 3 things to stimulate your baby\n###\nConcept: importance of meditation in the morning\nImage description: Picture of person doing yoga\nText to appear: /"
    prompt_text = f'{restart_sequence}: {inputText}{start_sequence}'
    response = get_open_ai_completion().create(
        engine="davinci-instruct-beta",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.9,
        max_tokens=300,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1,
        stop=["###"]
    )
    Output = response['choices'][0]['text']
    Design_prompt = f'Image description:{Output}'

    return Design_prompt


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getDesign_Meme(inputText):
    start_sequence = "\nImage description:"
    restart_sequence = "\n###\nConcept:"
    session_prompt_initial = "Given a Concept, generate a creative meme image description and text to appear\n\nConcept: Rappers\nImage description: Spiderman point meme with famous rappers head\nText to appear: Rappers when they say other rappers are liars\n###\nConcept: Food delivery\nImage description: Leonardo Dicaprio Django meme with food delivery\nText to appear: Me when I convince myself that I will cook dinner\n###\nConcept: Dentist\nImage description: Dentist working on patient's mouth\nText to appear: Dentist: Open up please  - Me: Sometimes I get sad\n###\nConcept: Student\nImage description: Student doing its nail in front of a computer \nText to appear: Me waiting for assignment to type itself\n###\nConcept: Dentist\nImage description: Guy screaming meme\nText to appear: Mom: the dentist isn't so bad - Kid in the other room:\n###\nConcept: Rappers\nImage description: Thinker meme\nText to appear: I'm trying to be a rapper but I can't afford the heavy chains\n###\nConcept: Insurance / Car\nImage description: Man and wife in bed\nText to appear: Her: He's probably thinking about other girls  - Him: Do Transformers have car insurance or life insurance?\n###\nConcept: Fitness / Gym\nImage description: Picture of OnePunchMan at the gym \nText to appear: Me after I go once at the gym\n###\nConcept: Car\nImage description: Spiderman pointing fingers meme\nText to appear: When my suspension cause handling issue, and my handling causes suspension issue\n###\nConcept: Vegan\nImage description: Man in a car crash interviewed by a journalist\nText to appear: Journalist: How do you feel - Man in windshield: Well, first of all, I'm vegan\n###\nConcept: Fitness\nImage description: Kermit the frog weight lifting \nText to appear: Me when I tell myself that I need to go back out for one more set.\n###\nConcept: Healthy eating\nImage description: Change my mind meme\nText to appear: It's not healthy food that sucks, it's you who don't know how to cook- Change my mind\n###\nConcept: Home cooking\nImage description: Ultra instinct meme\nText to appear: Me when I turn off the microwave 1 seconds before it goes off\n###\nConcept: Dating\nImage description: Picture of a skeletton\nText to appear: When your crush text you back 5 hours later.\n###\nConcept: Burger / Junk food restaurant\nImage description: Leonardo Dicaprio fat Django meme eating a burger\nText to appear: Me 2 hours after convincing yourself you'll eat healthier\n###\nConcept: Hair style\nImage description: Picture of a lego boy\nText to appear: Me when I style my hair by myself\n###\nConcept: Food\nImage description: Pablo escobar waiting meme\nText to appear: Me in front of my fridge waiting for new food to spawn\n###\nConcept: Computer / Gaming\nImage description: Picture of a triangle with on each corner a computer, a fridge and a bed\nText to appear: The real Bermuda triangle\n###\nConcept: Barbershop\nImage description: Awkward look meme\nText to appear: Me when I'm at the barber and hear the people in the chairs next to me engaging in conversations about their lives\n###\nConcept: Fitness\nImage description: Chubby kid at the pool saying \"Fitness is my passion\"\nText to appear: Me when I only eat 3 out of the 4 tacos I ordered\n###\nConcept: Noodle Restaurant\nImage description: Cat at table meme\nText to appear: Me when the fancy restaurant doesn't have noodles"
    prompt_text = f'{restart_sequence}: {inputText}{start_sequence}'
    response = get_open_ai_completion().create(
        engine="davinci-instruct-beta",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.9,
        max_tokens=200,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1,
        stop=["###"]
    )
    Output = response['choices'][0]['text']
    Design_prompt = f'Image description:{Output}'

    return Design_prompt


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getDesign_Portrait(inputText):
    start_sequence = "\nImage description:"
    restart_sequence = "\n###\nConcept:"
    session_prompt_initial = "Given a Concept, generate an image description and text to appear\n\nConcept: Alex, the co-founder of Smartflats who used to be a real estate agent\nImage descritpion: Picture of Alex in a brand coloured background\nText to appear : Have you met ... Alex ?\n###\nConcept: Thomas, the bike mecanics, who worked 20 years in the field\nImage description: Thomas in front of a bike with parts on the table smiling at the camera\nText to appear: /\n###\nConcept: Lucas, founder of Pitaya\nImage description: Picture of Lucas on a brand coloured background\nText to appear: /\n###\nConcept: Carole, the therapist and owner of the brand\nImage description: Carole on brand coloured background\nText to appear: Who am I ?\n###\nConcept: Raphaella, owner of Grant properties and real estate agent\nImage description: Raphaella crossing her arms in front of the camera and smiling on a brand coloured background\nText to appear: /\n###\nConcept: Cyril and David, co-founders of Madlab. Cyril is responsible of the production of the crackers and David is the head of sales\nImage description: Picture of Cyril and David smiling at the camera, Cyril holding a plate of crackers and Cyril eating one straight of the plate\nText to appear: /\n###\nConcept: The mom and daughter owners of Modus Vivendi\nImage description: Picture of the mom sitting on a couch and the daughter next to her sitting on of the couch's arm\nText to appear: /\n###\nConcept: Andrei, economics student and community manager of Saabou\nImage description: Andrei sitting on his computer with a camera next to him and surrounded by Saabou's products\nText to appear: /\n###\nConcept: Maxime, Co-founder of Snikpic and in charge of the web development\nImage description: Picture of Maxime in front of a laptop smiling at the camera\nText to appear: /"
    prompt_text = f'{restart_sequence}: {inputText}{start_sequence}'
    response = get_open_ai_completion().create(
        engine="davinci-instruct-beta",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.9,
        max_tokens=300,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1,
        stop=["###"]
    )
    Output = response['choices'][0]['text']
    Design_prompt = f'Image description:{Output}'

    return Design_prompt


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getDesign_Promotion(inputText):
    start_sequence = "\nImage description:"
    restart_sequence = "\n###\nConcept:"
    session_prompt_initial = "Given a Concept, generate a creative image description and text to appear\n\nConcept: Store summer promo\nImage description: Picture of a woman in summer clothing in our store purchasing a lot of products\nText to appear: Beach, please !\n###\nConcept: Whey yogurt\nImage description: Picture of the yoghurt pot next to whey powder in brand color background\nText to appear: No whey !\n###\nConcept: Onion flavoured cracker\nImage description: Picture of our onion flavoured cracker on brand colour background\nText to appear: Cry me a river\n###\nConcept: Strawberry flavoured coffee\nImage description: Picture of our strawberry flavoured coffee on brand colour background\nText to appear: Love you berry much\n###\nConcept: Whale themed t-shirt\nImage description: Picture of a man wearing our t-shirt with a suspicious look\nText to appear: Whale, whale, whale  - What do we have here ?\n###\nConcept: Summer dress\nImage description: Picture of a woman wearing our summer dress from the back walking away in the sun\nText to appear: Girls just wanna have sun\n###\nConcept: Babyzen stroller\nImage description: Picture of a woman pushing our babyzen stroller like riding a motorbike and sitting in the air\nText to appear: They see you strollin'\n###\nConcept: Avocado toast meal\nImage description: Picture of our avocado toast on a table with some avocadoes\nText to appear: You guac my world\n###\nConcept: Honey pot\nImage description: Picture of our honey pot on a tree like a bee nest with bees buzzing around it\nText to appear: To bee or not to bee ?\n###\nConcept: Energetic tea\nImage description: Picture of our tea on a brand colour background with some fireworks\nText to appear: Let's get this par-TEA started\n###\nConcpet: Puressentiel's stress roller\nImage description: Picture of our stress roller on brand colour background\nText to appear: Stress is more\n###\nConcept: Steak meal\nImage description: Picture of our steak meal in our restaurant\nText to appear: Love meat tender\n###\nConcept: Vegetarian restaurant in Brussels\nImage description: Picture of our restaurant in Brussels\nText to appear: Sprout to be in Brussels\n###\nConcept: Pho dish\nImage description: Picture of our Pho dish against the backlot of a Vietnamese market\nText to appear: Pho real\n###\nConcept: Bakery\nImage description: Picture of the bakers in the store make love sign with hands\nText to appear: All you knead is love\n###\nConcept: Anti-dandruff shampoo\nImage description: Picture of our shampoo on brand colour background\nText to appear: Made from scratch\n###\nConcept: Duck burrito\nImage description: Picture of our pulled pork burrito with some rice on a brown paper background\nText to appear: Quack-amole\n###\nConcept: Chicken Bahn mi sandwich\nImage description: Picture of our Banh mi sandwich on a brown paper\nText to appear: Please stand Banh mi\n###\nConcept: Beef Bo Bun\nImage description: Picture of our Bo Bun with beef on the plate on a green garden background\nText to appear: Hanoi-ingly good"
    prompt_text = f'{restart_sequence}: {inputText}{start_sequence}'
    response = get_open_ai_completion().create(
        engine=DAVINCI_INSTRUCT_BETA,
        prompt=session_prompt_initial + prompt_text,
        temperature=0.9,
        max_tokens=200,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1,
        stop=["###"]
    )
    Output = response['choices'][0]['text']
    Design_prompt = f'Image description:{Output}'

    return Design_prompt


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getDesign_Quote(inputText):
    start_sequence = "\nImage description:"
    restart_sequence = "\n###\nConcept:"
    session_prompt_initial = "Given a Concept, generate a creative image description and text to appear\n\nConcept: Fun fact about hairs\nImage description: Textual fact on brand predefined template\nText to appear: The average head contains over 100,000 hair follicles\n###\nConcept: Inspirational quote on beauty\nImage description: Quote on brand predefined template\nText to appear: Beauty is power; a smile is its sword - John Ray\n###\nConcept: Fun quote about women\nImage description: Quote on brand predefined template\nText to appear: I'm not a spender, I reward myself - It's different !\n###\nConcept: Inspirational quote on sleep\nImage description: Quote on brand predefined template\nText to appear: Sleep-care is the new self-care\n###\nConcept: Inspirational quote about life\nImage description: Quote on brand predefined template\nText to appear: Live your life in colors\n###\nConcept: Fun fact about dental care\nImage description: Textual fact on brand predefined template\nText to appear: Coconuts can help reduce the risk of developing gum disease and cavities.\n###\nConcept: Fun fact about Skin care\nImage description: Textual fact on brand predefined template\nText to appear: We shed about 30,000 to 40,000 skin cells per minute\n###\nConcept: Inspirational quote on work-life balance and family\nImage description: Quote on brand predefined template\nText to appear: If you want your children to turn out well, spend twice as much time with them and half as much money. —Abigail Van Buren\n###\nConcept: Fun fact for student\nImage description: Textual fact on brand predefined template\nText to appear: The average person spend on average 3 hours a day doing a useless activity\n###\nConcept: Fun quote about chinese food\nImage description: Quote on brand predefined template\nText to appear: Always in the mood - For Chinese food\n###\nConcept: Fun quote about recruitment \nImage description: Quote on brand predefined template\nText to appear: You don't have to be crazy to work here - We'll train you !\n###\nConcept: Inspirational quote about hustle\nImage description: Quote on brand predefined template\nText to appear: Work harder than you think you did yesterday"
    prompt_text = f'{restart_sequence}: {inputText}{start_sequence}'
    response = get_open_ai_completion().create(
        engine="davinci-instruct-beta",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.7,
        max_tokens=100,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1,
        stop=["###"]
    )
    Output = response['choices'][0]['text']
    Design_prompt = f'Image description:{Output}'

    return Design_prompt


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getDesign_News(inputText):
    start_sequence = "\nImage description:"
    restart_sequence = "\n###\nConcept:"
    session_prompt_initial = "Given a Concept, generate a creative image description and text to appear\n\nConcept: Opening of our new pharmacy in Ixelles\nImage description: Picture of the team cutting a red ribbon in front of our Ixelles pharmacy\nText: New pharmacy in Ixelles !\n###\nConcept: Celebrating our support to the belgian national football team\nImage description: Picture of the team cheering and laughing dressed as football supporter\nText to appear: /\n###\nConcept: French rapper Booba attacks rapper Youssoupha after the defeat of the french national football team on Euro 2020\nImage description: Collage picture of Booba next to Youssoupha with lightning in between and Euro 2020 logo below\nText to appear: /\n###\nConcept: Prince Harry and Meghan Markle new baby's name is Lili\nImage description: Meghan Markle holding Lili in her arm next to Harry\nText to appear: /\n###\nConcept: Release of the new Yoyo stroller line in store\nImage description: Picture of store with many Yoyo strollers\nText to appear: New in store\n###\nConcept: The team welcome Alex, a new barber\nImage description: Picture of Alex crossing arms and holding scissors in front of a barber chair\nText to appear: /\n###\nConcept: Summer sales\nImage description: Picture of line of people in the store with a big sign that says \"Summer sales\"\nText to appear: /\n###\nConcept: Christmas celebration\nImage description: Picture of the team dressed with ugly christmas sweaters\nText to appear: /\n###\nConcept: Back to school\nImage description: Picture of a team member bringing their kids to school\nText to appear: /\n###\nConcept: Birthday of Christelle\nImage description: Picture of Christelle in front of a cake surrounded by the team\nText to appear: /"
    prompt_text = f'{restart_sequence}: {inputText}{start_sequence}'
    response = get_open_ai_completion().create(
        engine="davinci-instruct-beta",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.7,
        max_tokens=100,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1,
        stop=["###"]
    )
    Output = response['choices'][0]['text']
    Design_prompt = f'Image description:{Output}'

    return Design_prompt


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getContentCategory(alt_text, caption):
    start_sequence = "\nCategory:"
    restart_sequence = "\n###\nalt-text:"
    start_sequence_caption = "\nCaption:"
    session_prompt_initial = "alt-text: food and text that says 'OMEGA'.\nCaption: What is omega-3? 👇\n\n\nIt is an essential fatty acid with many functions. Omega-3s:\n\n\n✅ Make up the membranes of all our cells and provide flexibility.\n✅ Play a role in the proper functioning of the heart and arteries\n✅ Increase bone density and decrease inflammation caused by osteoarthritis\n✅ ...\n\n\nOur body cannot produce. So we have to get it from other channels: food or supplements. Diet-wise, you can find it in nuts and fatty fish like salmon and tuna 🥜🐟 \n\nCategory: Information\nTopic: the importance of omega-3\n###\nalt-text: cosmetics and text.\nCaption: Have you visited the promo section on the site yet? 🤔🔥 Link in bio!\nCategory: Promotion\nTopic: our new promo section\n###\nalt-text: food\nCaption: 🤗Calling all the cheese lovers out there, Madlab proudly brings you Crackers & Cheese! 🤍\n\nWhy need junk foods when these Crackers & Cheese give you an equally tasty experience!\n\nBest served with a soup or a glass of your favorite wine, Crakers and Cheese matches them well. 😋🍪🌿\n\nGrab a bag for the family. We’re sure the kids and adults at home will love them, too. 😋 #madlab\nCategory: Promotion\nTopic: our \"Crackers & Cheese\" product\n###\nalt-text: indoor.\nCaption: Happy #laborday from @madlab.brussels. 💪 Enjoy the holidays @behere.be sustainable village with your family.\n\nAnd you can also gift a box of crackers and biscuits to your amazing coworker and show them how much you appreciate their efforts. 🎊 🎉\nCategory: News\nTopic: Labor day\n###\nalt-text: 2 people, child, body of water and text.\nCaption: 💧 Water holds a great value in Thailand! During Songkran -happening this April- you can have water fights and holy rituals and during summer you can explore crystal clear beaches where you go scuba diving. 🏖️\n\nNot to mention that keeping the title of largest exporter of rice requires a lot of water. So let’s celebrate #waterday! 🥳\nCategory: News\nTopic: Water day\n###\nalt-text: 2 people, people standing and indoor.\nCaption: 💥🎁GIVEAWAY🎁💥\nwin 2 menus consisting of the Magret Thai dish signed Chef Michel Sarran to be worth in one of our PITAYA restaurants!\nCategory: Promotion\nTopic: our Magret Thai dish\n###\nalt-text: 1 person, food and indoor.\nCaption: Who let the dog out, who, who, who, who 🐶\n\nThanks @mariondn_ for these lovely pictures!\nCategory: Inspiration\nTopic: our customers\n###\nalt-text: indoor.\nCaption: Today is yet another exciting day for us here at MAD LAB. 🥳\n\nMAD LAB is introducing its brand new e-shop, your go-to address for a variety of crackers, biscuits and dips to choose from! 💻\nGo explore our new digital home, and if you fancy saying hello in realtime, give us a call or shoot us an email. 📧 Cyril and David are all yours for personal assistance....But we’re not Amazon (and we don’t want to be), as we are doing honest business and don’t exploit the mailmen and women, you won’t receive your parcel within crazy timeframe.\n\n📲: https://www.madlab.brussels/boutique/\nCategory: News\nTopic: our brand new e-shop\n###\nalt-text: body of water and tree.\nCaption: Finally a little summer air these last few days ☀️\nCategory: Inspiration\nTopic: Summer\n###\nalt-text: outdoors.\nCaption: Wednesday Escape 🍋- Dreaming of sitting under the lemon tree in Italy at @casaangelinalifestyle via @uniquehotels\nCategory: Inspiration\nTopic: wednesday escape\n###\nalt-text: 1 person\nCaption: Meet Kubra 👩‍🍳👈\n\nIn charge of Mad Lab’s production, Kubra makes sure the crackers and biscuits arrive properly at your home.\n\nShe’s MADly good at what she does and we love her for it! Thank you, Kubra!\nCategory: Portrait\nTopic: Kubra\n###\nalt-text: 1 person and text that says '-Evening I'm cooking. -ME AT 20 HOURS. CHAMAS TACOS'.\nCaption: Who recognizes themselves? 🙌 🤣\nCategory: Meme\nTopic: Cooking\n###\nalt-text: text that says 'RAPPERS WHO SAY THAT OTHER RAPPERS ARE LIARS:'.\nCaption: Right? 🤣🤣🤣\nCategory: Meme\nTopic: Rappers\n###\nalt-text: text that says 'I don't spend money, I reward myself. That's different!'.\nCaption: It's only natural to reward yourself after a busy week 😉\nCategory: Quote\nTopic: rewarding yourself\n###\nalt-text: text that says 'You are your only limit! Flairbelgique'.\nCaption: Yes! When you want it, you can do it 😉\nOf course, that doesn't mean that everything will be easy. 💁🏼♀️\nCategory: Quote\nTopic: Anything is possible \n###\nalt-text: image of 1 person and text that says 'WHEN THE SHIT HITS THE FAN BUT AT LEAST YOU'RE WITH YOUR BEST FRIEND'.\nCaption: 🙌🤣\nTag your best buddy in a comment 👇\nCategory: Meme\nTopic: Friendship\n###\nalt-text: text that says 'indok The beauty of the sky is in the stars. The beauty of women is in their hair. OLIVIER Dachkin'.\nCaption: If you have any doubts, come by the salon without an appointment.\nCategory: Quote\nTopic: Women's hair\n###\nalt-text: text that says 'YOU ARE THE SUN'.\nCaption: Be a ray of sunshine wherever you go! 🌞\nCategory: Quote\nTopic: Being a sunshine\n###\nalt-text: 1 person and text that says 'What is EFT? A'.\nCaption: EFT (Emotional Freedom Technique) was developed by Gary Craig.\nThis technique consists of treating emotional disturbances through verbal enhancement and the stimulation of certain meridians.\nCategory: Information\nTopic: EFT\n###\nalt-text: drink and indoor.\nCaption: Let’s finish this long day!! Rain or shine, our margaritas are sure to satisfy 😎\nCategory: Inspiration\nTopic: Margaritas\n###\nalt-text: text that says 'Elegance is neither a question of coat rack nor a question of wallet. Karl Lagerfeld.'\nCaption: What do you think elegance is?\n\nWe look forward to your answers in the comments. 👇\nCategory: Quote\nTopic: Elegance"
    prompt_text = f'{restart_sequence}: {alt_text}{start_sequence_caption}{caption}{start_sequence}'
    response = get_open_ai_completion().create(
        engine="curie",
        prompt=session_prompt_initial + prompt_text,
        temperature=0,
        max_tokens=30,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###"]
    )
    Category = response['choices'][0]['text']
    Output = f'Category:{Category}'
    return Output


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getIntent(inputText):
    start_sequence = "\nIntent:"
    restart_sequence = "\n\nText:"
    session_prompt_initial = "Given a text, classify it within one of the following specific category:\n\n- makeAppointment\n- newRequest\n- changeRequest\n- giveInfo\n- getInfo\n- giveFeedback\n- noIntent\n- getHelp\n\n##\n\nText: Can you please add +32 468 08 52 06 to the discussion ?\nIntent: newRequest\n\nText: 30/3 promo article => I'm going to make this weekend a small video max 1 minute or 1 photo with the promo outfit. 01/04 => we can say something like 'this is not an april fool' and I announce that during the confinement there is 10% on La Croisette and Bellita + any purchase during the confinement gives the right to a tombola with 2x 50€ to win (draw at the end of the confinement of course) I'm going to prepare a visual support on Canva. 03/04 ok, photo or mini video \nIntent: changeRequest\n\nText: For the 15th,  we should post about the stand up event that we will have together with Kings of Comedy. I will try to have a photo for you and the information that should be shared. The rest is great. We can always say in the post that other matches will be broadcasted as well. \nIntent: newRequest\n\nText: Thanks <SM> ! Great basis of work!. Some generic comments : please keep paying attention to the timing (sometimes meal pictures are posted with a timing in the copy (for lunch,  Thursday, . . . ) while this is not matching to the actual timing of the post upload. In the file the Namur opening is not on the right day,  this will be crucial to us to have it posted on the right day.  I will of course keep you updated if this day changes. . same of labour day (saturday) . . .  water day . . . . I had for exemple to change the copy of today because it was written for your lunch while posted at 4pm. as I like a lot the post planned for Saturday,  would be great to double check that is it correctly planned with a timing of upload around 10am\nIntent: giveFeedback\n\nText: Hello, a little remark about the contest:1. It's not better to adopt a different strategy on fb and insta? 2. Is it voluntary not to put an end date? Thx\nIntent: getInfo\n\nText: How long does it take to see the result of a campaign ?\nIntent: getInfo\n\nText: Hello there 😊<AM> , I just looked at the \"Linktree\" homepage. I'm really not a fan. I'm not saying the image is ugly, far from it. Unfortunately, it doesn't match the branding of <Brand> . We don't (at least at this time) use illustrations. Also, in my opinion, the CTAs with that ripped effect and even the font used have nothing to do with our world\nIntent: giveFeedback\n\nText: It's already better. But I must admit that I'm a bit disappointed with the shooting, the pictures made are almost unusable in all honesty. The photos are awful.\nIntent: giveFeedback\n\nText: Hi <AM> , I see that 603. 78 euros have been debited already. Would it be possible please to get an invoice for this as well as a clear course structure? We are an ASBL and work with public funds so have to justify all our expenses. Thank you! <Client>\nIntent: getInfo\n\nText: Weren't we supposed to have a post today ? When is the next post ?\nIntent: getInfo\n\nText: Hi <AM>, how is the facebook ad campaign going. Is there a report on what is being done, if there are new campaigns that have been launched and if there are any trends that are emerging?\nIntent: getInfo\n\nText: 01/06 -> Let's change the picture please\nIntent: changeRequest\n\nText: How long is the strategy?\nIntent: getInfo\n\nText: An influencer contacted me on Instagram, what do I do?\nIntent: getInfo\n\nText: I don't want to collaborate with @Sophie, she doesn't fit our brand identity\nIntent: giveFeedback\n\nText: What is the contract I received by email?\nIntent: getInfo\n\nText: Our brand is vegan and must have green colors\nIntent: giveInfo\n\nText: Sorry I didn’t manage to come back to you today.  I will get on to this first thing tomorrow. . \nIntent: noIntent\n\nText: Hello, how are you?\nIntent: noIntent\n\nText: Yes of course! Not them. <SM>  or <AM> . But the person who worked for us one year ago. Sha has changed yesterday morning the password. And she changed the mail and number for phone. Number. I never think something like this about <AM>  or <SM>\nIntent: getHelp\n\nText: I prefer to stop all this now and come back to you I'm sorry thank you for emailing me what I need to do so that things are clear and I don't expect bills and I can make a payment plan with everything I have to do thank you in any case for everything you have done I hope we meet again soon\nIntent: changeRequest\n\nText: two packages have been sent, sistersandspice and Nora Dumoulin\nIntent: giveInfo\n\nText: Hi, you asked meabout dark humour, here a good example easily translatable into the food industry (sorry it's in french, I'll translate it if needed) : https://youtu.be/Q4RmJZS18f0\nIntent: giveInfo\n\nText: Keep the one for saturday. A feedback, real quick. 1 Talk more about our values 2 Our hashtag is #we are mad. I sent examples 2 weeks ago, let's take the last one with snoop dog.  You can have a pic with bunch of people having a party, eating crackers, drinking wine. Happy people, happy moments. Then, the day after, one of them, laying on the couch, huge hangover, in pyjama's with again a bag of crackers, line \"Nigel crackerss, cure the hangover\", stuff like that.\nIntent: giveFeedback\n\nText:  Hi, you asked me about dark humour, here a good example easily translatable into the food industry (sorry it's in french, I'll translate it if needed) : https://youtu.be/Q4RmJZS18f0\nIntent: giveInfo"
    prompt_text = f'{restart_sequence}: {inputText}{start_sequence}'
    response = get_open_ai_completion().create(
        engine="curie-instruct-beta",
        prompt=session_prompt_initial + prompt_text,
        temperature=0,
        max_tokens=64,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\n"]
    )
    Intent = response['choices'][0]['text']
    Output = f'Intent:{Intent}'
    return Output


def getIntentNLPCloud(inputText):
    client = nlpcloud.Client("xlm-roberta-large-xnli", Settings.NLP_CLOUD_ID_TOKEN)
    classification_result = client.classification(inputText, NLP_CLOUD_LABELS)

    labels = [intent.replace(' ', '') for intent in classification_result['labels']]
    intent = labels[0]

    scores = classification_result['scores']
    logger.debug(f"{tuple(zip(labels, scores))}")

    return f'Intent: {intent}'


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getSubjectEntities(inputText):
    start_sequence = "\nList:\n"
    restart_sequence = "\n\n##\n\nbrand type:"
    session_prompt_initial = "Given a text, provide the subject and entity\n\n##\n\nText: Can you please add +32 468 08 52 06 to the discussion ?\nSubject: Add Member\nEntity: +32 468 08 52 06\n\n\nText: 30/3 promo article => I'm going to make this weekend a small video max 1 minute or 1 photo with the promo outfit. 01/04 => we can say something like 'this is not an april fool' and I announce that during the confinement there is 10% on La Croisette and Bellita + any purchase during the confinement gives the right to a tombola with 2x 50€ to win (draw at the end of the confinement of course) I'm going to prepare a visual support on Canva. 03/04 ok, photo or mini video \nSubject: Publication\nEntity: 30/3 - 03/04\n\n\nText: For the 15th,  we should post about the stand up event that we will have together with Kings of Comedy. I will try to have a photo for you and the information that should be shared. The rest is great. We can always say in the post that other matches will be broadcasted as well. \nSubject: Publication\nEntity: 15th\n\n\nText: Thanks <SM> ! Great basis of work!. Some generic comments : please keep paying attention to the timing (sometimes meal pictures are posted with a timing in the copy (for lunch,  Thursday, . . . ) while this is not matching to the actual timing of the post upload. In the file the Namur opening is not on the right day,  this will be crucial to us to have it posted on the right day.  I will of course keep you updated if this day changes. . same of labour day (saturday) . . .  water day . . . . I had for exemple to change the copy of today because it was written for your lunch while posted at 4pm. as I like a lot the post planned for Saturday,  would be great to double check that is it correctly planned with a timing of upload around 10am\nSubject: Publication\nEntity: /\n\n\nText: Hello, a little remark about the contest:1. It's not better to adopt a different strategy on fb and insta? 2. Is it voluntary not to put an end date? Thx\nSubject: General\nEntity: contest, strategy\n\n\nText: How long does it take to see the result of a campaign ?\nSubject: General\nEntity: campaign\n\n\nText: Hello there 😊<AM> , I just looked at the \"Linktree\" homepage. I'm really not a fan. I'm not saying the image is ugly, far from it. Unfortunately, it doesn't match the branding of <Brand> . We don't (at least at this time) use illustrations. Also, in my opinion, the CTAs with that ripped effect and even the font used have nothing to do with our world\nSubject: Page\nEntity: Linktree, CTA\n\n\nText: It's already better. But I must admit that I'm a bit disappointed with the shooting, the pictures made are almost unusable in all honesty. The photos are awful.\nSubject: Photo Shoot\nEntity: /\n\n\nText: Hi <AM> , I see that 603. 78 euros have been debited already. Would it be possible please to get an invoice for this as well as a clear course structure? We are an ASBL and work with public funds so have to justify all our expenses. Thank you! <Client>\nSubject: Invoice\nEntity: /\n\n\nText: Weren't we supposed to have a post today ? When is the next post ?\nSubject: Publication\nEntity: today, next post\n\n\nText: Hi <AM>, how is the facebook ad campaign going. Is there a report on what is being done, if there are new campaigns that have been launched and if there are any trends that are emerging?\nSubject: Facebook Ad\nEntity: campaign, report\n\n\nText: 01/06 -> Let's change the picture please\nSubject: Publication\nEntity: 01/06\n\n\nText: How long is the strategy?\nSubject: General\nEntity: strategy\n\n\nText: An influencer contacted me on Instagram, what do I do?\nSubject: Influencer\nEntity: contact\n\n\nText: I don't want to collaborate with @Sophie, she doesn't fit our brand identity\nSubject: Influencer\nEntity: @Sophie\n\n\nText: What is the contract I received by email?\nSubject: General\nEntity: contract\n\n\nText: Our brand is vegan and must have green colors\nSubject: Brand\nEntity: vegan, green colors\n\nText: Sorry I didn’t manage to come back to you today.  I will get on to this first thing tomorrow. . \nSubject: /\nEntity: /\n\n\nText: Hello, how are you?\nSubject: /\nEntiy: /\n\n\nText: Yes of course! Not them. <SM>  or <AM> . But the person who worked for us one year ago. Sha has changed yesterday morning the password. And she changed the mail and number for phone. Number. I never think something like this about <AM>  or <SM>\nSubject: Access\nEntity: password, mail, number for phone\n\n\nText: I prefer to stop all this now and come back to you I'm sorry thank you for emailing me what I need to do so that things are clear and I don't expect bills and I can make a payment plan with everything I have to do thank you in any case for everything you have done I hope we meet again soon\nSubject: Contract\nEntity: /\n\n\nText: two packages have been sent, sistersandspice and Nora Dumoulin\nSubject: Influencer\nEntity: sistersandspice, Nora Dumoulin\n\n\nText: Hi, you asked me about dark humour, here a good example easily translatable into the food industry (sorry it's in french, I'll translate it if needed) : https://youtu.be/Q4RmJZS18f0\nSubject: General\nEntity: dark humour"
    prompt_text = f'{restart_sequence}: {inputText}{start_sequence}'
    response = get_open_ai_completion().create(
        engine="curie-instruct-beta",
        prompt=session_prompt_initial + prompt_text,
        temperature=0,
        max_tokens=64,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\n\n"]
    )
    Output = response['choices'][0]['text']
    SubjectEntities = f'Subject:{Output}'

    return SubjectEntities


def getPostIdeas_common(brand_type, period):
    start_sequence = "\nList:\n"
    restart_sequence = "brand type:"
    period_sequence = "\nperiod:"

    prompt_text = f'{restart_sequence} {brand_type}{period_sequence} {period}{start_sequence}'

    response = openai.Completion.create(
        model="davinci:ft-snikpic:concept-generator-2022-03-09-11-55-31",
        prompt=prompt_text,
        temperature=0.7,
        max_tokens=250,
        top_p=1,
        best_of=3,
        frequency_penalty=0.2,
        presence_penalty=2,
        stop=["##"]
    )
    PostIdeas = response['choices'][0]['text']
    PostIdeas = PostIdeas.replace("<br>", "\n")
    PostIdeas = PostIdeas.replace("\t", "\n")
    pattern = r"[0-9]+[.][ ]([A-z ]+)[-][ ](.*)|[-][ ]([A-z ]+)[:](.*)"
    sentences = [text for text in PostIdeas.split("\n") if text]
    dict_of_sentences = []
    for s in sentences:
        result = re.findall(pattern, s)
        try:
            result = [r for r in result[0] if r != ""]
            type_ = result[0].strip()
            description = result[1].strip()
            dict_of_sentences.append({"type": type_, "description": description}) if result else None
        except Exception as err:  # TODO: dangerous, remove this!!!
            # print(err)
            pass

    return dict_of_sentences


@retry((PermissionError, openai.error.RateLimitError), tries=5, delay=2, backoff=2)
def getPostIdeas(brand_type, period):
    res = getPostIdeas_common(brand_type, period)
    return res


def get_name_quote(line):
    m = re.compile("[\s\d.]+([^:]+):(.+)").match(line)

    if not m:
        return None
    second_part = m.group(2).strip()
    pattern = re.compile(r'[^—–-]+')
    partitioned_second_part = pattern.findall(second_part)

    if len(partitioned_second_part) < 2:
        logger.warning(f"Failed to find author, assigning it to {UNKNOWN_AUTHOR}; line: {line}")
        if len(partitioned_second_part) < 1:
            return None

        author_name = UNKNOWN_AUTHOR
    else:
        author_name = (partitioned_second_part[-1]).strip()

    quote_type = (m.group(1)).strip()
    name = f"{author_name} ({quote_type})"

    quote = ('-'.join(partitioned_second_part[:-1])).strip('“”"\' ')
    return name, quote


def parse_quote_concept(concepts: str):
    compiled_check_first = re.compile("\s*\d+\.")

    concept_list = []
    splitted = concepts.strip().split("\n")
    last_index = len(splitted) - 1
    saved_line = ''
    for i, line in enumerate(splitted):
        line = line.strip()

        if compiled_check_first.match(line):
            if saved_line:
                name_quote = get_name_quote(saved_line)
                if not name_quote:
                    logger.warning(f"Failed to parse concept: {saved_line}")
                    continue
                concept_list.append(name_quote)

                saved_line = ""
        saved_line += line

        if i == last_index:
            name_quote = get_name_quote(saved_line)
            if not name_quote:
                logger.warning(f"Failed to parse concept: {saved_line}")
                continue
            concept_list.append(name_quote)

    res = [{"name": name, "description": quote, "date": None, "links": [], "score": 1}
           for (name, quote) in concept_list]
    return res


def get_post_ideas_switcher_function(concept: PostIdeasCategory):
    switcher = {
        PostIdeasCategory.information: getconcept_information,
        PostIdeasCategory.promotion: getconcept_promotion,
        PostIdeasCategory.inspiration: getconcept_inspiration,
        PostIdeasCategory.quotes: getconcept_quotes,
    }
    res = switcher.get(concept)
    return res


def extend_concept_list(res, category, saved_line):
    res.append({
        "name": category,
        "description": saved_line.partition('.')[2].strip(),
        "date": None,
        "links": [],
        "score": 1
    })


def parse_general_concept(category: PostIdeasCategory, concepts: str):
    res = []

    compiled = re.compile("\s*\d+\.")
    splitted = concepts.split('\n')
    last_index = len(splitted) - 1

    saved_line = ''
    for i, s in enumerate(splitted):
        if compiled.match(s):
            if saved_line:
                extend_concept_list(res, category, saved_line)  # print the previous sentence as it is ended
                saved_line = ""
        saved_line += s

        if i == last_index:
            extend_concept_list(res, category, saved_line)
    return res


def parse_calendar_events(events, year, month, day):
    date = f"{year:02}-{month:02}-{day:02}"

    return [
        {'name': event['name'],
         'description': event['excerpt'].strip(),
         'date': date,
         'links': [event['url']],
         'score': 0}
        for event in events
    ]


def parse_past_events(events):
    res = [
        {'name': event['description'],
            'description': '\n'.join(event['contexts']) if event['contexts'] else '',
            'date': event['date'],
            'links': event['links'],
            'score': event['score']}
        for event in events['events']
    ]
    return res


def parse_deaths_births(events):
    births = [
        {'name': 'births - ' + event['description'],
            'description': '\n'.join(event['contexts']) if event['contexts'] else '',
            'date': event['date'],
            'links': event['links'],
            'score': event['score']}
        for event in events['births']
    ]
    deaths = [
        {'name': 'deaths - ' + event['description'],
         'description': '\n'.join(event['contexts']) if event['contexts'] else '',
         'date': event['date'],
         'links': event['links'],
         'score': event['score']}
        for event in events['deaths']
    ]
    return births + deaths


async def calendar_events(  # copy-pasted from event_recs.py
        desc: str,
        year: int,
        month: int):
    """
    Return a list of events for a given description.

    - If day == 0 : returns scored monthly events only
    - If day is None, returns scored monthly and daily events
    """
    events: List[Dict] = []

    logger.debug("started getting events")

    # get list of events for the specific month
    # in the list-of-lists format
    monthly_events = await date_year_month(year, month)

    for i in range(len(monthly_events)):
        events += parse_calendar_events(monthly_events[i]['data'], year, month, i)

    logger.debug("result has %d events entries" % len(events))

    # Get the events similarity scores from the Private Api
    scores = get_event_scores(desc, [event['description'] for event in events])

    events_to_return = []
    for index in np.argsort(-np.array(scores)):
        # update score
        events[index]['score'] = scores[index]
        events_to_return.append(events[index])
    return events_to_return


async def clip_prefix_caption_ai(image: UploadFile) -> str:
    logger.debug(f"{image.filename} is being processed")
    bytes_context_image = BytesIO(image.file.read())
    res = replicate_version.predict(image=bytes_context_image)
    logger.debug(f"context_image processed")
    return res


async def clip_prefix_caption_ai_downloaded(bytes_context_image: bytes) -> str:
    logger.debug(f"Downloaded image is being processed")
    bytes_context_image = BytesIO(bytes_context_image)
    res = replicate_version.predict(image=bytes_context_image)
    logger.debug(f"context_image processed")
    return res


async def clip_prefix_caption_ai_ws(context_image: bytes) -> str:
    logger.debug(f"context_image is being processed")
    bytes_context_image = BytesIO(context_image)
    res = replicate_version.predict(image=bytes_context_image)
    logger.debug(f"context_image processed")
    return res


async def get_post_ideas_v2_ai(category: PostIdeasCategory, brand_type, period, context_string: str,
                               context_image: Optional[UploadFile] = File(None),
                               context_image_url=None,
                               context_image_alternative=None) -> List[Dict]:
    logger.debug(f"{category}, {brand_type}, {period}, {context_string}, "
                 f"{getattr(context_image, 'filename', None) if context_image else None}",
                 f"{context_image_url}")
    if context_string:
        description = get_hybrid_description(brand_type, context_string)
        logger.debug(f"get_hybrid_description: description: {description}")
    elif context_image:
        generated_context_string = await clip_prefix_caption_ai(context_image)
        logger.debug(f"{context_image.filename} {generated_context_string}")
        description = get_hybrid_description(brand_type, generated_context_string)
        logger.debug(f"get_hybrid_description: description: {description}")
    elif context_image_alternative:
        generated_context_string = await clip_prefix_caption_ai_ws(context_image_alternative)
        logger.debug(f"context_image_alternative {generated_context_string}")
        description = get_hybrid_description(brand_type, generated_context_string)
        logger.debug(f"get_hybrid_description: description: {description}")
    elif context_image_url:
        downloaded_context_image = requests.get(context_image_url).content
        generated_context_string = await clip_prefix_caption_ai_downloaded(downloaded_context_image)
        logger.debug(f"downloaded_context_image, {generated_context_string}")
        description = get_hybrid_description(brand_type, generated_context_string)
    else:
        description = brand_type
    get_concept_function = get_post_ideas_switcher_function(category)
    if get_concept_function is not None:
        # convert month number to month name
        month_name = datetime.strptime(str(period), "%m").strftime("%B").lower()
        # add new field to each dict
        res = get_concept_function(description, month_name)
        logger.debug(f"get_concept_function: res: {res}")
        if category == PostIdeasCategory.quotes:
            res = parse_quote_concept(res)
            logger.debug(f"parse_quote_concept: res: {res}")
        else:
            res = parse_general_concept(category, res)
            logger.debug(f"parse_general_concept: res: {res}")
    else:
        if category == PostIdeasCategory.portrait:
            births_deaths = get_past_events(["births", "deaths"], period, description, True, 10)
            logger.debug(f"get_past_events: births_deaths: {births_deaths}")
            res = parse_deaths_births(births_deaths)
            logger.debug(f"parse_deaths_births: res: {res}")
            if len(res) < 20:
                logger.error(f"Not enough births and deaths were found ({len(res)}): {res}.")
        elif category == PostIdeasCategory.calendar_events:
            res = await calendar_events(description, date.today().year, period)
            if len(res) < 10:
                logger.error(f"Not enough calendar events were found ({len(res)}): {res}.")
            res = res[:10]
            logger.debug(f"calendar_events: res: {res}")
        elif category == PostIdeasCategory.past_events:
            births_deaths = get_past_events(["events"], period, description, True, 10)
            logger.debug(f"get_past_events: births_deaths: {births_deaths}")
            res = parse_past_events(births_deaths)
            logger.debug(f"parse_past_events: res: {res}")
        else:
            raise AIProcessingException(f"Unsupported category: {category}")
    return res


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getBio(brand_name, brand_type, brand_objective):
    sequence_1 = ", a "
    sequence_2 = " which main objective is to "
    sequence_3 = "\nBio:"

    session_prompt_initial = "Write the Instagram bio for a the following brands\n\nMADLAB (ww.madlab.brussels), a manufacturer and seller of organic crackers and biscuits in Belgium which main objective is to convert online shoppers\n\nBio:\n🍪 = 🌱 + ♻️ + a 🥄 of MADness 🤪\nMade in 🇧🇪 with 🥰\n#weareMAD\nwww.madlab.brussels\n\n##\n\nAncho (www.ancho.be),  a high-end mexican restaurant in Brussels (Louise, Woluwe, Saint Boniface) which main objective is to convert into physical store visit\n\nBio:\nFor the Mexican way of life & the Ancho chili\nInspirations from Baja California to NYC\nLouise, Woluwe, Saint Boniface\nwww.ancho.be\n\n##\n\nBees-Api Bruxelles (www.beesapibxl.be), an urban beekeeping and sale of honey products and by-products, which main objective is to convert online shoppers\n\nBio:\nBRUSSELS BEEKEEPER 🐝🍯🇧🇪\nFROM THE BEEKEEPER TO THE CONSUMERS\n100% Belgian honey, 100% natural 🌿\nFind our products at ⤵️\nwww.beesapibxl.be\n\n##\n\nOlivier Dachkin (www.olivierdachkin.com), a chain of hair salons in Belgium for mature women, which main objective is to convert into physical store visit\n\nBio:\nAn incomparable style ✨\nThe hair salons ⬇️\nwww.olivierdachkin.com\n\n##\n\nFines Herbes (finesherbes.be), a company organizing catered events for companies, weddings and private events with elegance and authenticity, which main objective is generate leads online\n\nBio:\nElegance and wonder\nWhatever the occasion 🍾💍✨\nShort circuit in Wallonia 💚🍀\nQuestions? Send a message!\nwww.finesherbes.be\n\n##\n\nMelkior (www.melkiorprofessional.fr), a professional quality make-up brand sold in Belgium, which main objective is to convert online shoppers\n\nBio:\nAccessible luxury 💋\nOne goal: to make you even more beautiful 🤩🏆\n👇🏻👇🏼👇🏾 Tips and eShop\nwww.melkiorprofessional.fr\n\n##\n\nO'Nouilles, a restaurant of Noodles in Charleroi with large portions and large choices of sauces, which main objective is to convert into physical store visit and online orders\n\nBio:\n🌏 Sauces from the 4 corners of the world...\n🥡 ... Viking-sized portions\n📍 Charleroi\n🛵 UberEats, Deliveroo, Takeaway\n\n##\n\nL'ATYPIQ, world fusion and gourmet tacos restaurant for breakfast, lunch, aperitif and dinner in Brussels, which main objective is to convert into physical store visit\n\nBio:\n🌮 Gourmet tacos\n🗺️ Inspired from the 4 corners of the world\nBreakfast, lunch, aperitif, dinner\n\n##\n\nTeddyVit, a heathly candies for kids and adults to reinforce immune system, help sleep, good for health, which main objective is to engage audiences on Instagram\n\nBio:\nNatural & veggie vitamins for kids 🌿🏆\nImmunity, Sleep, Health… 💪😴🎯\nFrom 🇧🇪\n📍 In all pharmacies and para-pharmacies\n\n##\n\nErnest Restaurant, a restaurant with terrace and brunch place in the park of the Chateau de la Hulpe, Belgium, which main objective is to convert into physical store visit\n\nBio:\nTo eat with colleagues, friends or family. 🍽 🥐\n🏰 Chateau de la Hulpe, Belgium\n📍 112 Av. Ernest Solvay, La Hulpe\n\n##\n\n"
    prompt_text = f'{brand_name}{sequence_1}{brand_type}{sequence_2}{brand_objective}{sequence_3}'

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.7,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["##"]
    )
    InstaBio = response['choices'][0]['text']

    return InstaBio


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getHook(caption):
    restart_sequence = "\nCaption:\n"
    start_sequence = "\n\nHook:"

    session_prompt_initial = "For a given caption, create a catching Hook\n\nCaption:\nOmega-3s are essential fatty acids that have several functions:\n✅ Provide flexibility to all our cells to improve our heart and arteries\n✅ Increase bone density and decrease inflammation caused by osteoarthritis\n✅ Slow down the degeneration of brain cells and help strengthen memory\n✅ ...\n\nFoods rich in omega-3 are nuts and fatty fish like salmon and tuna 🥜🐟\n\nHook:\nTop 3 reasons why Omega-3s are the best for your health\n\n##\n\nCaption:\nWe are opening a new restaurant in Antwerp, May 11th. 🆕\n\nTo get a free dish, be one of the first 100 customers at Melkmarkt 28, 2000 Antwerp. We open at 11.30 A.M.!\n\nWe can’t wait for you to taste our fabulous thai food. 🍲\n\nHook:\nIf you want to a free meal, you need to see this\n\n##\n\nCaption:\nAn angel dropped by and blessed us with this unique dish. 🦐🦐\n\nThis tasty dish created by Marie Ange came from the best woker competition of PITAYA. 🤌\n\nAvailable in all of our restaurants now!?\n\nHook:\nPeople will hate me for saying this but this is the best shrimp wok dish\n\n##\n\nCaption:\nAs they say: after a hard day’s work, take comfort in good Mexican cuisine! 🇲🇽\n\nWe’re waiting for you!\n\nHook:\n If you want to relax after a work day, here's what you need to do\n\n##\n\nCaption:\nDo you know what a real modern gentleman is?\n\nThe True Gentleman is the man whose conduct proceeds from good will and an acute sense of propriety, and whose self-control is equal to all emergencies; who does not make the poor man conscious of his poverty, the obscure man of his obscurity, or any man of his inferiority or deformity; who is himself humbled if necessity compels him to humble another; who does not flatter wealth, cringe before power, or boast of his own possessions or achievements; who speaks with frankness but always with sincerity and sympathy; whose deed follows his word; who thinks of the rights and feelings of others, rather than his own; and who appears well in any company, a man with whom honor is sacred and virtue safe.\n\nCome visit us to reveal the gentleman inside You 🙌🏻\n\n\nHook:\nWhat nobody tells you about modern gentleman\n\n##\n\nCaption:\nMAD LAB X FAIRE\n\nWe've partnered with Faire to sell our wholesale products online. 📲\n\nAs professional, you can now buy our crackers online on Faire and get 300€ off and 1 year of free shipping ! 💶\n\nLink : https://madlabbrussels.faire.com/\n\nHook:\nIf you are a professional and want 300€ off our products, you need to see this\n\n##\n\nCaption:\nHappy Easter from the entire Madlab team! 🐰\n\nHook:\nThis is what happens when you celebrate Easter with Madlab\n\n##\n\nCaption:\nLet's talk with Kenza 😊\n\nKenza was a one-month intern at Mad Lab. Student at ICHEC Business Management School, she was in charge of Glimpact @glimpact_eu\n\nYou don't know what it is ? 🤔\n\nThis organisation contributes to the challenges of ecological transition by helping businesses to evaluate their environmental impact.\nIt applies the PEF (Product environmental foodprint) method adopted by the European Union.\nThrough it, businesses are able to modify their products or services in order to reduce their environmental impact. ♻️\n\nWatch this interview to know more about Kenza and her internship 👆🏻\n\nHook:\n\nYou won't believe what Kenza's previous job was\n\n##\n"
    prompt_text = f'{restart_sequence}{caption}{start_sequence}'

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=session_prompt_initial + prompt_text,
        temperature=1,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\n##"]
    )
    Hook = response['choices'][0]['text']

    return Hook


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getSpellCheckFrench(caption):
    response = openai.Edit.create(
        engine="text-davinci-edit-001",
        input=caption,
        instruction="Corriger ce texte (ortographe, grammaire, vocabulaire, ponctuation, liasons, conjugaison, accord des pluriels, etc.)",
        temperature=0,
        top_p=1
    )
    Newcaption = response['choices'][0]['text']

    result = {"spell_checked_text": Newcaption}

    return result


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getImprovedFormat(caption):
    response = openai.Edit.create(
        engine="text-davinci-edit-001",
        input=caption,
        instruction="change the format: line breaks, repeated strings, etc.",
        temperature=0,
        top_p=1
    )
    Newcaption = response['choices'][0]['text']

    return Newcaption


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getEditCaption(caption, edit):
    response = openai.Edit.create(
        engine="text-davinci-edit-001",
        input=caption,
        instruction=edit,
        temperature=0,
        top_p=1
    )
    Newcaption = response['choices'][0]['text']

    return Newcaption


@retry((PermissionError,), tries=5, delay=2, backoff=2)
def getAdCopy(inputCTA, inputBrandDesc, inputKeyfeature, inputAudience, inputBrandName, InitialisationDic):
    headline_sequence = "\nAd Headline:\n"
    description_sequence = "\nAd Description:\n"
    primary_sequence = "\nAd Primary Text:\n"
    restart_sequence = "\n###\nBrief:"
    session_prompt_intro = "Given a Brief, generate an Ad Headline, Description and Primary Text"
    session_prompt_initial = ""
    session_prompt_initial += f'{session_prompt_intro}'
    session_brief_desc = " for a "
    session_brief_kf = " that offers "
    session_brief_audience = " targeting "
    session_brief_name = " named "
    for i in range(len(InitialisationDic)):
        session_prompt_initial += f"{InitialisationDic[i]['Brief']}{headline_sequence}" \
                                  f"{InitialisationDic[i]['Headline']}{description_sequence}{InitialisationDic[i]['Description']}{primary_sequence}{InitialisationDic[i]['Primary']}{restart_sequence}"
    prompt_text = f'{session_prompt_initial}{inputCTA}{session_brief_desc}{inputBrandDesc}{session_brief_kf}{inputKeyfeature}{session_brief_audience}{inputAudience}{session_brief_name}{inputBrandName}'

    response = get_open_ai_completion().create(
        engine="text-davinci-002",
        prompt=prompt_text,
        temperature=0.65,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0.8,
        presence_penalty=0.3,
        stop=["###"]
    )
    AdCopy = response['choices'][0]['text']

    return AdCopy


def getBR(description, user_story):
    start_sequence = "\nBusiness Rules:\n"
    restart_sequence = "\nDescription:"
    period_sequence = "\nUser Story:"

    prompt_text = f'{restart_sequence} {description}{period_sequence} {user_story}{start_sequence}'

    session_prompt_initial = "Given the application Description and User Story , provide Business Rules\n\nDescription:  All-in-one tool to allow marketing agencies to manage and automate their workflow\nUser Story: As a user part of an organization (Manager or team member), I want to be able to view and filter the tasks\nBusiness Rules:\n- User can filter by : Status, Type, Brand, Task name\n- The user can sort by due date in ascending or descending order\n- By default the filter and sorting should be : (i) If the user is a team member they should see all their open tasks (assigned to them) order by ascending due date (A team member should not have access to the tasks assigned to other team members in any case. They should see only their tasks) , (ii) If the user is a Manager, they should see all the tasks order by ascending due date\n###\n"

    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.5,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###"]
    )
    BR = response['choices'][0]['text']

    return BR


# get-prompt


def getprompt_food(description):
    start_sequence = "\nPrompt:"
    restart_sequence = "\nDesc:"

    prompt_text = f'{restart_sequence} {description}{start_sequence}'

    session_prompt_initial = "Transform image description into DALL-E prompt\n\nDesc: Chocolate fondant in a nice plate\nPrompt: Chocolate fondant, Michelin Star restaurant quality, minimalist, Zeiss Master Prime 50mm photography, soft and moody lighting, Digital Food, 35mm Photograph\n##\nDesc: Big burger\nPrompt: big juicy burger, depth of field, food photography, uplight, isometric, studio, bokeh, gmaster, cooking, food, kodak, sony, canon, bright colorful highlights, Digital Food \n##\nDesc: Chocolate waffle\nPrompt: Chocolate waffle, product photography sessions, studio light, 4k \n##\nDesc: Medium rare cooked steak and coke on a wooden table\nPrompt: professional macro photography of Medium rare cooked steak and coke, centered in frame, on a rustic wooden surface, back lit natural daylight, beautiful bokeh\n##\nDesc: Hot dog\nPrompt: photo of an icelandic hot dog with a steamed bun, fresh onion, crispy onion, lamb frankfurter, remoulade, ketchup and mustard\n##\nDesc: top view of a ramen dish\nPrompt: Flatlay realistic photo of delicious ramen, highly detailed, natural light, 8 k hd, award winning, artstation\n##\nDesc: homemade bread\nPrompt: homemade bread realistic photo shoots, Stock photos, article illustration, website illustrations\n##\nDesc: croissant\nPrompt: beautiful freshly baked croissant on a table in a French bakery, studio lighting, professional culinary photography, focus, Nikon 85mm, very detailed, high quality\n##\nDesc: salad with tomatoes, leafy greens, croutons and shredded cheese in a white bowl on a wood table\nPrompt: Photograph of a salad with tomatoes, leafy greens, croutons, and shredded cheese, in a white bowl on a wood table, even mid-key light\n##\nDesc: michelin-star pancake\nPrompt: Portrait of a michelin-star pancakes, professional food photography, captivating, rule of thirds, majestic, octane render\n##\nDesc:  peperonni pizza\nPrompt: photograph of fresh italian peperonni pizza served on a wooden cutting board, photorealistic, detailed, shallow depth of field, award-winning professional food photography, 15mm, featured in Food & Wine Magazine, trending on Reddit\n##"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.8,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["##"]
    )
    prompt = response['choices'][0]['text']

    return prompt


def getprompt_portrait(description):
    start_sequence = "\nPrompt:"
    restart_sequence = "\nDesc:"

    prompt_text = f'{restart_sequence} {description}{start_sequence}'

    session_prompt_initial = "Transform image description into DALL-E prompt\n\nDesc: women with long blond hair\nPrompt: A photo portrait of a female supermodel, soft neutral expression, long blond hair, symmetrical face, front facing, looking at camera, studio lighting, 8k. Dramatic, professional photography. UHD.\n##\nDesc: dramatic black and white photo of an old man\nPrompt: Photo of an old man, editorial shoot , 8k, Dramatic, professional photography, UHD , high-contrast black and white, detailed eyes, Lee Jeffries\n##\nDesc: White samoyed dog wearing a cowboy hat in the city\nPrompt: Portrait of a dog,  samoyed/white,  wearing a cowboy hat,  city in the background , professional photo, Luke Kaven\n##\nDesc: cinematic photo of a slim teenage girl at night\nPrompt: Film still of slim girl, 20yo, soft neutral expression, symmetrical face, colorful lighting, cinematic, night, 8K, professional photography, UHD, detailed eyes, Bill Sienkiewicz\n##\nDesc: Asian women with blue eyes, purple lips and short black hairs with a bright background\nPrompt: A photo portrait of a beautiful asian female supermodel, blue eyes, full purple lips, intense short black hair, looking at camera, studio lighting, 8k, professional photography. bright background. UHD. vintage filter\n##\nDesc: male with long red hair and blue eyes in purple and blue neon light on a dark background\nPrompt: A  photo portrait of a male supermodel, blue eyes, long red hair, looking at camera, neon purple and blue lighting, detailed eyes, studio lighting, 8k, professional photography. dark background. UHD. \n##\nDesc: young women holding a siamese cat\nPrompt: beautiful young woman portrait with a single light color background, closed eyes, and a siamese cat, Nikon D810 f/1.8-f/5.6\n##\nDesc: pinup nurse with green eyes\nPrompt: \"Ana de Armas from Bladerunner 2049 (2017)\" as a \"tantalizing pinup nurse\" with \"green eyes and dark coiffed hair lounging at her station\" in a \"classic white uniform\" wearing \"a closed teasing smile\", \"airbrushed golden hour portrait photography by Annie Leibovitz\"\n##\nDesc: silver hair dragon queen\nPrompt: \"a tantalizing baroque portrait photograph by Annie Leibovitz\" \"Ana de Armas from Bladerunner 2049 (2017)\" \"dragon queen from Game of Thrones\" \"lounging on her medieval fantasy throne\", \"long coifed silver hair, serious, young, elegant, golden dragon-horn styled tiara, rubies, dragon themed jewelry\", 4k, cinematic lighting\n##\nDesc: African man with beard and long hair\nPrompt: A real photography of a man's face,  African, beard, long hair, beautiful Photorealistic Portrait, studio light, soft light, Vogue\n##\nDesc: old timey mobster\nPrompt: 1940s mobster mugshot, wearing hat, scar, old photograph, Kodak Retina II, f/2 Schneider Kreuznach Xenon\n##\nDesc: face closeup\nPrompt: face, portrait, translucent, 8k, highly detailed, closeup, macro photo, highly detailed, cinematic lighting, realistic, 70mm\n##\nDesc: man yelling at someone over the phone\nPrompt: Film still of man yelling over the phone, anger expression, symmetrical face, professional photo, cinematic scene, atmospheric perspective, detailed eyes, 8k, hyper realistic, studio ligthing, cinematic, night, 8K, professional photography, UHD\n##\nDesc: Artistic black and white photo of a lion\nPrompt: Lion, editorial shoot, high-contrast black and white, featured in Vogue\n##\nDesc: hippopotamus in savanah\nPrompt: Wildlife photography of a hippopotamus , safari photography, 85 mm lens, award winning pulitzer prize winning photograph by Cristina Mittermeier in National Geographic Magazine.\n##"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.65,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["##"]
    )
    prompt = response['choices'][0]['text']

    return prompt


def getprompt_object(description):
    start_sequence = "\nPrompt:"
    restart_sequence = "\nDesc:"

    prompt_text = f'{restart_sequence} {description}{start_sequence}'

    session_prompt_initial = "Transform image description into DALL-E prompt\n\nDesc: Porsche car\nPrompt: portrait of a Porsche, ambient studio lighting, hyperrealism, 8k uhd, Hajime Sorayama\n##\nDesc: Lion plush on a wood stool with green grass and spring flowers\nPrompt: portrait of a lion plush,35mm, golden hour, warm lighting, soft, cuddly, happy,  close-up, small, colorful fur, glossy black eyes, whimsical and cartoon-like, sitting on a patch of raised lush green grass, bokeh, spring flowers, animal crossing, sitting on a tiny wooden stool, tilted frame, Anaïs Bordier\n##\nDesc: red high heel shoe \nPrompt: red high heel shoe product photo, dark moody lighting movie, blurred reflectant black water rippling floor foreground, high-contrast dark background, bright colorful highlights, 8k, hyper realistic, thomas anderson\n##\nDesc: render of a futuristic vehicle on a circular platform\nPrompt: A 3D render of a futuristic vehicle, on a circular platform, with terrain at a distance, octane rendering, ultra HD, ultra detailed, Syd Mead\n##\nDesc: Teddy bear with a mohawk wearing punk clothing\nPrompt: 3D render of a Teddy bear with a mohawk wearing punk clothing, Monsters inc, pixar animation digital art, octane rendering, ultra HD, ultra detailed, Sully, Atsuya Uki\n##\nDesc: colourful asian streetwear hoodie\nPrompt: A product concept image of a 6-tone all-over vibrant color streetwear hoodie with kanji asian characters, in dope hip hop style, poisonous caterpillar design, street wear concept art render, korean street fashion, ultra realistic details, vaporware style, 3d concept render, 40 mm wide lens centered\n##\nDesc: white yeezy sneakers\nPrompt: Professional detailed picture of 3D realistic white sneakers designed by yeezy, with hyperdetailed realistic textures. placed afar at the center of an all-white room with professional lights.\n##\nDesc: design red and black chair\nPrompt: Bauhaus brno chair, high quality material, red and black, cubik, minimal lines, function, photorealistic, 3d rendering, 1920s, german artist, white background\n##\nDesc: magenta balloon in the shape of a letter H\nPrompt: photo of 3D \"H\" , inflated magenta balloon material, glossy, bright studio lighting, front view, no crop, white background, rendered in octane, trending on behance, highly detailed, 8k, sharp,\n##\nDesc: lego fireman next to his truck\nPrompt: a LEGO fireman and a LEGO fire truck in a lego city, LEGO fireman has two identical eyes, 8k, uhd, octane render high quality\n##\nDesc: kitchen titanium pot\nPrompt: a floating kitchen chef's knife rendered in maya, trending, white background, hi-def, cartoonish, designed by cuisinart, single, by itself, made of gel, vibrant, award winning\n##\nDesc: Nail art with summer colors and black background\nPrompt: Closeup of a simple gel nail art manicure in summer colors, with hands flat and centered, Cinematic shot, Overhead shot, high detail, black background, 8k, hyper realistic, Hikari Shimoda\n##\nDesc: miniature globe of new york city at night in autumn\nPrompt: mini floating NYC night cityscape with grass, trees, and flowers, Autumn leaves floating on a rock under a round glass globe, floating on geological rock, hover, levitate, bubble, skyline, city landscape, isolated on white, center vertical aligned, architecture, built structure, downtown, tower, urban scene, outdoors, clipping, path, professional photography, Wide-Angle, Leica, Nisi filter, Canon, 75mm 1/75, long exposure\n##"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.65,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["##"]
    )
    prompt = response['choices'][0]['text']

    return prompt


def getprompt_icon(description):
    start_sequence = "\nPrompt:"
    restart_sequence = "\nDesc:"

    prompt_text = f'{restart_sequence} {description}{start_sequence}'

    session_prompt_initial = "Transform image description into DALL-E prompt\n\nDesc: burger gradient\nPrompt: burger-icon, synthwave vector art, gradients, vibrant color, 8K, featured on 99designs\n##\nDesc:  3D glowing ice cream\nPrompt: 3D icon of a lightly glowing ice cream, dark background, logo style, digital art\n##\nDesc: modern musical note gradient\nPrompt: musical note iconic gradient filled modern 2D shiny smooth bevel logo, solid white background\n##\nDesc: e-sport style lion\nPrompt: an angry lion head wearing a backwards hat on a neon background, e-sports logo vector, 2d flat, hyper quality digital art, Trending on Artstation, centered,\n##\nDesc: black and yellow battle rooster shaped like an \"F\"\nPrompt: Professional high quality Dribbble black and yellow 3D icon-logo design of the letter \"F\" shaped as a detailed battle rooster. Centered on a white paper texture background.\n##\nDesc: peace sign sketch\nPrompt: Illustration logo of a peace sign by Da Vinci, sketch, drawn with pencil, very clear lines, high detailed, featured on 99designs\n##\nDesc: unicorn in blue gradient\nPrompt: a blue gradient unicorn head with a gold horn, looking to the left, vibrant color, 8K, featured on 99designs\n##\nDesc: 3D red glowing \"S\" letter shaped as infinite sign\nPrompt: Professional high quality 3D icon of a lightly red glowing \"S\" letter shaped as infinite sign on a dark background, 8k, logo style, digital art, high quality Dribbble\n##\nDesc: elephant head doodle\nPrompt: a doodle scandi of an elephant head. minimalist, geometric, line art, from the portfolio of an award winning designer. svg, vector illustration, black background\n##\nDesc: 3d pizza\nPrompt: a tiny, cute 3d pizza icon for a food app. high quality 3d render, cinema 4d, floating in the air against a deep background\n##\nDesc: 3d yellow frowning emoji on a red background\nPrompt: a small 3d yellow frowning emoji on a plain red background, high quality 3d render, centered in frame\n##\nDesc: Stylized typo of \"love\"\nPrompt: \"LOVE\", design by dribbble, accurate detailed professional typography by dan mumford\n##"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.65,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["##"]
    )
    prompt = response['choices'][0]['text']

    return prompt


def getprompt_scene(description):
    start_sequence = "\nPrompt:"
    restart_sequence = "\nDesc:"

    prompt_text = f'{restart_sequence} {description}{start_sequence}'

    session_prompt_initial = "Transform image description into DALL-E prompt\n\nDesc: Red brick city alley at night in the rain with a reflective puddle in the front\nPrompt: Looking down a red brick city alley at night in the rain with a reflective puddle in the foreground, 2 point perspective, professional photo, cinematic scene, atmospheric perspective, 8k, hyper realistic, high-contrast dark background, bright colorful highlights, Bruce Gilden\n##\nDesc: wintertime landscape with a cathedral and mountain\nPrompt: walking through the bavarian alps, in the winter time, a tiny bavarian cathedral, godlight over cathedral, mountain corridor, mountain lake in distance, great finesse organic hyper detailed, beautiful, serene, cinematic, cinematography, landscape photography, realistic, 10mm lens, first person view, 16k, vfx, hyper photorealistic, cinematic, intricate detail, well lit, 3d, hyper realistic details, realism, volumetric bright lights, extremely sharp lines, post processing 4k, octane render, unreal engine 5, depth of field, Ansel Adams\n##\nDesc: futuristic living room with some plants\nPrompt: futuristic, curvilinear, interior, minimal living room, terracotta clay, arches, tall ceilings, white stucco, curved glass, lush prairie landscape , artificial lighting, green ivy, lush green botanicals, plants, succulents, all white environment, foggy,  with floating furniture, 8k video,  UHD,  3d rendering,   post processing 4k, Hajime Sorayama\n##\nDesc: sunset in nature\nPrompt: a photograph of a sunset in nature, cinematic, peaceful, serene, vibrant, epic, breathtaking, great finesse organic hyper detailed, 10mm lens, 16k, vfx, hyper photorealistic, cinematic, intricate detail, well lit, 3d, hyper realistic details, realism, volumetric bright lights, post processing 4k, octane render, unreal engine 5, depth of field\n##\nDesc: eerie backroom\nPrompt: A realistic rendered image of a gloomy backroom, which gives a feeling of suspense, with several rooms in the background, with dramatic lighting, that simulates the backrooms of dreams, 2 point perspective, professional photo, cinematic scene, atmospheric perspective, 8k, hyper realistic, high-contrast dark background, bright colorful highlights, Bruce Gilden\n##\nDesc: top of mountains at sunrise with river in between \nPrompt: a wide angle picture from the top of a mountain at the sunrise, in front of other mountains and a river that flows between them, great finesse organic hyper detailed, beautiful, serene, cinematic, cinematography, landscape photography, realistic, 10mm lens, first person view, 16k, vfx, hyper photorealistic, cinematic, intricate detail, well lit, 3d, hyper realistic details, realism, volumetric bright lights, extremely sharp lines, post processing 4k, octane render, unreal engine 5, depth of field, Ansel Adams\n##\nDesc: eerie moon at earth rise\nPrompt: wide angle picture from an eerie moon at earth rise, with earth in the background, which gives a feeling of suspense, 3d rendering,  2 point perspective, professional photo, atmospheric perspective, 8k, hyper realistic, post processing 4k\n##\nDesc: Stick stiched together like a can arch in a shallow pond\nPrompt: A professional photograph, Land art, Sticks mounted in a shallow pond, Stitched together and arranged like a can arch, Creating a perfect reflection in the water, Canon 5d mkII, 14mm, Wide shot, Natural lighting, Graduated filter\n##\nDesc: light shining through a forest\nPrompt: A beautiful light shines through the forest, Nikon D810, ISO 64, focal length 20mm (Voigtländer 20mm f3.5), Aperture f/9, Exposure Time 1/40 Sec (DRI)\n##"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.65,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["##"]
    )
    prompt = response['choices'][0]['text']

    return prompt


def getprompt_illustration(description):
    start_sequence = "\nPrompt:"
    restart_sequence = "\nDesc:"

    prompt_text = f'{restart_sequence} {description}{start_sequence}'

    session_prompt_initial = "Transform image description into DALL-E prompt\n\nDesc: Manga style drawing portrait of a pirate with a scar\nPrompt: Pirate portrait, manga style, drawing, intense stare, eye patch, scar, Akira Toriyama, UHD , vector art , sharp , 1px lines, behance , devianart\n##\nDesc: watercolor style of an eagle head\nPrompt: colorful eagle head, highly detailed, watercolor with paint splatter in the background, 8k, realistic, epic\n##\nDesc: blueprint of a rocket ship\nPrompt: A blueprint of rocket ship,  blue background, detailed, high precision\n##\nDesc: editorial style illustration of a hand holding a cigarette\nPrompt: illustration of a hand holding a cigarette. minimalist screenprint, saul bass vaporwave, paper texture\n##\nDesc: japanese style waves crashing on a beach\nPrompt: Japanese Ukiyo-e woodblock print depicting waves crashing on a beach, intricate and detailed, complex, edo period, kanji, ink, Japanese aesthetic, bright colors, highly stylized, Japanese Landscape, ethereal, detailed shadows, cinematic, realistic figures, accurate, octane render, 8k, photorealistic\n##\nDesc: psychedelic illustration of a goat\nPrompt: Hypnotic illustration of goat head, dark glow neon paint, mystical, intricate, hypnotic psychedelic art, pop surrealism, Dan Mumford\n##\nDesc: sketch of a karateka\nPrompt: A stylized depiction of karateka posing, ink, sketch, concept art, by artist Yoji Shinkawa, Kim Jung Gi, intricate and detailed, accurate, line art, metal gear solid concept art aesthetic, 2d, calligraphy, extremely realistic, hyper detailed\n##\nDesc: pencil drawing of a toddler boy with curly blond hair and blue eyes\nPrompt: Pencil drawing of a toddler boy with curly light blond hair and blue eyes, realistic, detailed, high precision\n##\nDesc: watercolor style illustration of a man screaming\nPrompt: Watercolor style illustration of a man screaming, intense and realistic, bright colors, highly detailed, watercolor with paint splatter in the background, 8k, realistic, epic\n##\nDesc: colourful sea otter mixing chemicals\nPrompt: A sea otter mixing colourful sparkling chemicals in a laboratory, digital art, bright colors, highly detailed\n##\nDesc: Magazine style illustration of a giraffe wearing hornrimmed glasses and a fedora\nPrompt: A magazine cover illustration of a profile portrait giraffe wearing hornrimmed glasses and a fedora, in a flat minimal style, bold split complimentary colors, white highlights, curvy shapes, clean lines, Color combinations create shadow and depth, Influences of cubism, digital art\n##"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.65,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["##"]
    )
    prompt = response['choices'][0]['text']

    return prompt


def getprompt_render(description):
    start_sequence = "\nPrompt:"
    restart_sequence = "\nDesc:"

    prompt_text = f'{restart_sequence} {description}{start_sequence}'

    session_prompt_initial = "Transform image description into DALL-E prompt\n\nDesc: block city\nPrompt: 3d isometric view cityscape diorama on a small square island floating in the void, view of a modern business district, golden hour, high detail, digital art\n##\nDesc: mini living room in pastel colors\nPrompt: Pastel colored isometric living room, high quality 3d render\n##\nDesc: blueprint of a rocket ship\nPrompt: A blueprint of rocket ship,  blue background, detailed, high precision\n##\nDesc: calendar icon\nPrompt: isometric 3d icon of a calendar in stock illustration style, 3d render, white background\n##\nDesc: toaster\nPrompt: toaster, isometric art, elegant, sophisticated, understated, pastel colors, artstation, 3D render, cgsociety, 8k uhd\n##\nDesc: pikachu\nPrompt: Digital art of Pikachu, white background, cute Pixar character, houdini 3D render\n##\nDesc: funko pop figurine of superman with a cape\nPrompt: a 3D render of a funko pop of superman, funko pop has a cape, funko pop is full body picture, picture has white background\n##\nDesc: cute cat\nPrompt: Cute fluffy animal, Cute goggly eyes, Unreal Engine 3D render, Trending on ArtStation, Realistic fur\n##\nDesc: mini version of a futuristic office building with solar panel \nPrompt: an isometric view of a 3d icon, diorama of a futuristic transdisciplinary designed solar focused office building, built on a single thin square shaped platform floating at a distance in a void, photorealistic, golden hour, 4k, sharp, clean\n##\nDesc: futuristic otter wearing blue\nPrompt: Portrait of a hyperrealistic and ultradetailed fat puppet sci-fi otter cute monster smiling with huge cute eyes, wearing a luminous blue futuristic elaborate VR dieselpunk headset as a backpack. with a gray grain background.\n##\nDesc: cute goth pineapple toy\nPrompt: 3d art of a very very very cute goth pineapple squishmallow design plush toy. 3d render on a colourful gradient background, deep shadows, studio photography\n##\nDesc: tulip with particle effect\nPrompt: rendering of a fluid glossy spiraling white tulip blossoming with mossy growth and spraying gold glitter in an all white environment\n##\nDesc: cute monster with googly eyes and purple fur\nPrompt: A 3D render of a cute monster with googly eyes and purple fur, standing in a white background, Unreal Engine 3D render, Trending on ArtStation, Realistic fur\n##\nDesc: Red panda\nPrompt: Red Panda, Portrait, Cinematic lighting, Volumetric lighting, Epic composition, Photorealism, Bokeh blur, Very high detail, Sony Alpha α7, ISO1900, Character design, Unreal Engine, Octane render, HDR, Subsurface scattering\n##\nDesc: unicorn skull in a field of flowers\nPrompt: A 3D rendering of a bleached unicorn skull sitting in a field of colorful flowers, Swirling horn, Colorful lighting, Mountains in the distance, Saturated colors, Trending on art station, Popular on Behance, C4D, Octane-render, 4K, 8K\n##"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.65,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["##"]
    )
    prompt = response['choices'][0]['text']

    return prompt


def getprompt_action(description):
    start_sequence = "\nPrompt:"
    restart_sequence = "\nDesc:"

    prompt_text = f'{restart_sequence} {description}{start_sequence}'

    session_prompt_initial = "Transform image description into DALL-E prompt\n\nDesc: rescue team of 4 people walking away from helicopter\nPrompt: Film still of a rescue team of 4 people, walking toward the camera, helicopter in the background, dramatic natural sunlight,  highly detailed, detailed eyes, 8k, F/22, RED camera, 35mm\n##\nDesc: ghost walking in a medieval japanese town\nPrompt: A ghostly figure walking through a medieval Japanese town at night, with paper lanterns and a red moon in the sky,  Japanese timber-framed minka buildings, wide angle 8k composite photograph, atmospheric art, hyper realistic, professional photo, 3D rendering, post processing 4k\n##\nDesc: over the shoulder view of a man watching television\nPrompt: over the shoulder stock photograph of a man watching television, cinematic lighting, Voigtlander Super Nokton 29mm f/0.8, Cinelux ASA 100\n##\nDesc: a white Ferrari driving in japan city at night\nPrompt: a long shot of a white Ferrari driving fast in a Japan city at night, background blurred by the motion, police car lights, Portra 800, early 2000s, side view, 4800K, full length photo\n##\nDesc: dramatic woman washing her face\nPrompt: A young woman is whing her face, Bathroom, Tired, Makeup, Pale, Curly hair, Award winning, Portrait by Lee Jeffries\n##\nDesc: old style photo of a relieved farmer in the mountains with his pigs\nPrompt: A close-up portrait of a relieved man with eyes closed, dirty skin, skinny ribs showing in chest, On a barren mountainside with a lake and mountains. a photo of Many many pigs running down a mountainside in the distance, Pigs in large dust cloud, Golden hour, On a barren mountainside with a lake and mountains in the distance, 50mm, F/22, Deep depth of field, Ilford HP5 400, Schindler's List (1993)\n##\nDesc: Tilt shift picture of New Yorkers getting on the subway\nPrompt: Tilt shift photography of New Yorkers getting on the subway, digital art\n##\nDesc: French woman taking a selfie in front of Devil's Tower\nPrompt: Film still of a very French woman is taking a selfie in front of Devil's Tower, Wyoming, detailed eyes, highly detailed, 8k, Nikon F3, 50mm, Kodak Gold 200\n##\nDesc: a robot hand serving coffee and cheese cake\nPrompt: close up photo of a highly detail robot hand, serving a tray with a cup of coffee and a piece of cheese cake, a stream of fume seeing on top of coffee cup, warm colors, natural sunlight, Zeiss medium format, 8k, Deep depth of field, 50mm, F/22\n##\nDesc: Chimpanzee sticking his head out of water full of purple flowers\nPrompt: A portrait of a chimpanzee with its face sticking out of the purple water full of flowers, hyper realism, highly detailed, 50mm, f1.8, low angle shot, 8k, Deep depth of field\n##\nDesc: An alien robot painting on a canvas in a grand baroque art studio\nPrompt: A cinematic photo of an alien robot painting on a canvas with his robot hands in a grand baroque art studio with luxurious chandeliers and marble sculptures, fog, dreamy lighting, chiaroscuro, 8k, F/22, 50mm, Deep depth of field\n##\nDesc: Santa Claus slipping on a house roof\nPrompt: Santa Claus slipping on a house roof, North Pole, Christmas, Santa's sleigh and reindeers in the background, night time, detail oriented, 8k, F/22, RED camera, 35mm\n##"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.65,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["##"]
    )
    prompt = response['choices'][0]['text']

    return prompt


def getimage(input, volume):
    response = openai.Image.create(
        prompt=input,
        n=volume,
        size="1024x1024"
    )

    image_urls = [item['url'] for item in response['data']]

    return image_urls


def get_hybrid_description(branddesc, imagedesc):
    start_sequence = "\nConcept:"
    brand_sequence = "\nBrand:"
    image_sequence = "\nImage:"

    prompt_text = f'{brand_sequence} {branddesc}{image_sequence} {imagedesc}{start_sequence}'

    session_prompt_initial = "Given a Brand description and an Image description, come up with a new brand Concept\n\nBrand: Thai food fast-food restaurant chain aimed at millennials\nImage: Edamame on a wooden background.\nConcept: Thai style edamame restaurant chain aimed at millennials\n##\nBrand: Japanese store that sells manga and figurines of anime\nImage: 3d cg rendering of a samurai\nConcept: Japanese store specialized in anime figurine of samurai\n##\nBrand: Belgian creative sauce brand for teenagers\nImage: a man cooking meat on a grill.\nConcept: Belgian sauce brand made for grills and barbecue\n##\nBrand: Healthy fast food where customers can customize their menu\nImage: man sitting at a table with a glass of iced coffee.\nConcept: Healthy store where customers can customize their iced coffee\n##\nBrand: Zero waste grocery store\nImage: customers shop at the newly opened coffee shop\nConcept: Grocery store that sells only sustainable and zero waste coffee in bulk\n##\nBrand: Club house with great Padel and Tennis courts\nImage: a glass of red wine and a bottle of white wine on a wooden table.\nConcept: Wine club with great Padel and Tennis courts\n##"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.7,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["##"]
    )
    hybrid = response['choices'][0]['text']

    return hybrid


def get_branddesc(description):
    restart_sequence = "\nDescription:\n"
    start_sequence = "\nWhat it is selling:\n"

    prompt_text = f'{restart_sequence} {description}{start_sequence}'

    session_prompt_initial = "From a Facebook business description, try to infer what the business is actually selling\n\nDescription:\nHealthy Living Made Easy\nGet the highest quality, healthy and sustainable products delivered at member-only prices. Start your risk-free membership today!\nWhat it is selling:\nDelivery membership for high quality, healthy and sustainable food products\n##\nDescription:\nKion is energy for life\nPure, science-backed formulas that enhance your body’s natural energy from all angles.\nWhat it is selling:\nNatural supplements to improve athlete's performance\n##\nDescription:\nTowels have two basic jobs: dry my naked body, and dry itself.\nSo why is it that most towels represent a compromise between softness, absorbency, and quickness to dry?\nMeet Onsen - the towel that works like its job depended on it.\nWhat it is selling:\nHigh quality towels that are soft, absorbent, and quick-drying.\n##\nDescription:\n#ToKnowThemIsToLoveThem\nNutrition, care, and love for exactly who your dog is.\nWhat it is selling:\nFreshly made food from real, human-grade ingredients, tailored to dog's unique nutritional needs\n##\nDescription:\nOur highly trained Sleep Experts® know how to match you with your perfect mattress. Rest assured, we've got your back.\nWhat it is selling:\nMattresses and mattress-related products and services such as mattress matching by Sleep Experts.\n##"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=session_prompt_initial + prompt_text,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["##"]
    )
    description = response['choices'][0]['text']

    return description


