import json
from app.core.translation import translate_text

from loguru import logger

logger.info(f'---{__name__}---')

from app.core.ai import getCaption, getDesign_Inspiration, getDesign_Information, getDesign_Meme, getDesign_Portrait, \
    getDesign_Promotion, getDesign_Quote, getDesign_News, getContentCategory, getIntent, getSubjectEntities

# INPUT

Category = 'Information'
postRequest = 'Healthy eating'
lang = 'EN'

# PROCESSING
function_name = f'getDesign_{Category}'
postRequest_translated = translate_text(postRequest, 'EN')
OutputDesign2 = eval(function_name + '(postRequest_translated)')
Text = json.dumps(OutputDesign2).replace('\\n', ' , ').replace('\"', "")
Dictionary = {i.split(': ')[0]: i.split(': ')[1] for i in Text.split(', ')}
Dictionary["Image description"] = translate_text(Dictionary["Image description"], lang)
Dictionary["Text to appear"] = translate_text(Dictionary["Text to appear"], lang)
logger.info(Dictionary)
