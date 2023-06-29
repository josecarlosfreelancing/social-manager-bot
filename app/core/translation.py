import os

from progress.bar import Bar
from loguru import logger
import deepl

from .extract_input import extractInputCSV
from .write_output import OutputCSV
from app.config import Settings


## TRANSLATING A SINGLE TEXT
def translate_text(textinput, targetlanguage):
    targetlanguage = 'EN-US' if targetlanguage == 'EN' else targetlanguage
    key = os.environ['DEEPL_API_KEY']
    # logger.debug("key: " + key)
    translator = deepl.Translator(key)

    r = translator.translate_text(textinput, target_lang=targetlanguage)
    return r.text


## TRANSLATING A FILE
async def translate_file(inputPath, outputPath, lang):
    input = extractInputCSV(inputPath)

    output = []
    with Bar('Translation...', max=len(input)) as bar:
        for items in input:
            translation = translate_text(items.values(), lang)
            output.append(translation)
            bar.next()

    OutputCSV(outputPath, output, "Output Text")
