import nltk
import re
import emoji
from collections import Counter
import deepl
import os

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.schemas import InstacaptionSchema

_ = nltk.download('punkt') # download nltk resource if its missing
instacaptions_router = APIRouter()


def preprocess_caption_(caption):

    raw_caption = caption
    caption_meta = {}
    caption = emoji.demojize(caption.strip())

    # count emojis
    emoji_counter = Counter()
    for em_ in re.findall(":[1-9a-zA-Z_-]+:", caption):
        emoji_counter[emoji.emojize(em_)] += 1

    # caption_meta['emoji_counts'] = emoji_counter
    caption_meta['total_emoji'] = sum(emoji_counter.values())
    caption_meta['unique_emoji'] = len(emoji_counter)
    caption_meta['emoji_list'] = list(emoji_counter.keys())

    # hashtag and mention regex
    hashtag_regex = "(?:#)([A-Za-zÀ-ú0-9_](?:(?:[A-Za-zÀ-ú0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-zÀ-ú0-9_]))?)$"
    mention_regex = "(?:^|[^\w])(?:@)([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)"

    filtered_text = lambda text:re.sub(hashtag_regex[:-1], '', re.sub(mention_regex, '', text))

    trail_end_hashtags = caption
    while re.findall(hashtag_regex, caption):
        caption = re.sub(hashtag_regex, '', caption).strip()
    trail_end_hashtags = trail_end_hashtags[len(caption):]

    caption = emoji.emojize(caption)

    # remove unemojized emojis
    caption = re.sub(":[a-zA-Z_-]+:", '', caption)
    # remove mentions
    # caption = re.sub("(?:^|[^\w])(?:@)([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)", '', caption)

    # remove appended underlines
    # caption = caption.replace('_', '')

    paragraphs = [p for p in caption.split('\n') if p]
    sents = []
    for paragraph in paragraphs:
        # remove extra spaces
        paragraph = re.sub('\s(\s+)', ' ', paragraph)
        for text in nltk.sent_tokenize(paragraph):
            if len(text)>=5 and len(set(text))>1: # short sents and sents comprised of single char
                sents.append(text.strip())

    translator = deepl.Translator(os.environ['DEEPL_API_KEY'])
    if sents:
        result = translator.translate_text(sents, target_lang="EN-GB")

        sent_langs = [r.detected_source_lang for r in result]
    else:
        sent_langs = []

    #check if len of sentence(without mentions and hashtags) is larger than a thresh
    for i in range(len(sents)):

        # filtered_text = re.sub(mention_regex, '', sents[i])
        # filtered_text = re.sub(hashtag_regex[:-1], '', filtered_text)

        if len(filtered_text(sents[i]))<=5:
            # sentence consisting of single mention/hashtag
            if re.findall(hashtag_regex[:-1], sents[i]):
                # set sentence's language to 'HASHTAG'
                sent_langs[i] = 'Hashtag'
            elif re.findall(mention_regex, sents[i]):
                # set sentence's language to 'HASHTAG'
                sent_langs[i] = 'Mention'

        # Update language of 'EN' sentences sorrounded by other languages
        if i>0 and i<len(sents)-1 and sent_langs[i]=='EN':
            # check the lang of sorrounding sents
            if sent_langs[i-1]==sent_langs[i+1]:
                sent_langs[i] = sent_langs[i-1]

    # merge sentences of same language
    def consec_lang(langs):
        for i in range(1, len(langs), 1):
            #check if lang same as previous one
            if langs[i]==langs[i-1]:
                return True
        return False

    sum_sentences = [1 for _ in sent_langs]
    while consec_lang(sent_langs):
        for i in range(1, len(sent_langs)):
            if sent_langs[i]==sent_langs[i-1]:
                # merge same langs
                sent_langs = sent_langs[:i-1] + sent_langs[i:]

                # concat corresponding sentences, merge
                # sents[i-1] += ' '+sents[i]

                # find the character(s) within the sentences in the raw caption
                intra_chars = "123456789"
                
                if sents[i-1] in raw_caption and sents[i] in raw_caption:
                    # calculating substring idx
                    idx = (raw_caption.index(sents[i-1])+len(sents[i-1]), raw_caption.index(sents[i]))

                    if idx[0]<idx[1]:
                        intra_chars = raw_caption[idx[0]:idx[1]]

                if len(intra_chars)>=7:
                    sents[i-1] += ' '+sents[i]
                else:
                    sents[i-1] += intra_chars + sents[i]

                sents = sents[:i] + sents[i+1:]

                # re-calculate sentence count list
                sum_sentences[i-1] += sum_sentences[i]
                sum_sentences = sum_sentences[:i] + sum_sentences[i+1:]

                break

    langs = {}
    sent_count = Counter()
    cnt = 0
    for s, l in zip(sents, sent_langs):
        if l not in langs:
            langs[l] = s
        else:
            langs[l] += " "+s

        sent_count[l] += sum_sentences[cnt]
        cnt += 1

    if langs:
        max_len_lang, max_len = sorted(langs.items(), key=lambda x:-len(filtered_text(x[1])))[0]

    # if no english text available, translate the first other language
    if 'EN' not in langs:
        if langs:
            l_to_translate = max_len_lang
            result = translator.translate_text(langs[l_to_translate], target_lang="EN-GB")

            langs['EN'] = str(result)
            sent_count['EN'] = sent_count[l_to_translate] 

        else:
            # add empty 'EN' lang
            langs['EN'] = ''
            sent_count['EN'] = 0 
    else:
        # check if length of the 'EN' sentences is shorter than a threshold

        if len(filtered_text(langs['EN']))<0.3*len(max_len):
            #merge 'EN' with translated max_len_lang
            result = translator.translate_text(langs[max_len_lang], target_lang="EN-GB")

            #check position of 'english' text compared to the other max_len_lang text

            if langs['EN'] in raw_caption and langs[max_len_lang] in raw_caption:
                en_index = raw_caption.index(langs['EN'])
                max_len_index = raw_caption.index(langs[max_len_lang])
                if en_index > max_len_index:
                    # en goes last
                    langs['EN'] = str(result) + " " + langs['EN']
                else:
                    # en goes first
                    langs['EN'] += " " + str(result)
            else:
                # check by referencing to the raw caption
                if langs['EN'] in raw_caption and raw_caption.index(langs['EN']) > 0.5 * len(raw_caption):
                    langs['EN'] = str(result) + " " + langs['EN']
                else:
                    langs['EN'] += " " + str(result)


    # move 'EN' language to the beggining of the list
    # and remove language CODES
    new_langs = {}
    for l in sorted(langs, key=lambda l: -1 if l=='EN' else 0):
        new_langs[l] = re.sub(r"\b(BG|CS|DA|DE|EL|EN|ES|ET|FI|FR|HU|IT|JA|LT|LV|NL|PL|PT|RO|RU|SK|SL|SV|ZH)\b[\s:]*", '', langs[l])
    langs = new_langs

    caption_meta['languages'] = langs
    caption_meta['sent_count'] = dict(sent_count)

    if len(trail_end_hashtags) > 2:
        caption_meta['trail_end_hashtags'] = trail_end_hashtags

    return caption_meta


def split_n_translate(accessib_caption):
    split_token = 'text that says '
    if split_token in accessib_caption:
        #split at token
        accessib_caption = accessib_caption.split(split_token)
        # first part is in english by default; translate second part
        first_part = accessib_caption[0]
        to_translate = accessib_caption[1]


        translator = deepl.Translator(os.environ['DEEPL_API_KEY'])
        to_translate = translator.translate_text(to_translate, target_lang="EN-GB")

        return first_part + split_token + str(to_translate)

    return accessib_caption


@instacaptions_router.post('/process_caption')
async def process_caption(text: InstacaptionSchema):
    result = process_caption_implementation(text.texts)

    json_compatible_item_data = jsonable_encoder(result)
    return JSONResponse(content=json_compatible_item_data)


@instacaptions_router.post('/process_accessib_cap')
async def send_data(text: InstacaptionSchema):
    result = split_n_translate(text.texts)

    return result
