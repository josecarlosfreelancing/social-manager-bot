import json
import time
from strenum import StrEnum
from types import CoroutineType
from typing import Optional
from json import dumps, loads
from loguru import logger
from fastapi import APIRouter, HTTPException, Query, status, UploadFile, File, BackgroundTasks, WebSocket
from fastapi.responses import JSONResponse, HTMLResponse
from openai.error import APIConnectionError, InvalidRequestError, APIError, TryAgain, Timeout, RateLimitError
from httpx import ConnectTimeout, ReadTimeout, HTTPError, HTTPStatusError, RequestError, TimeoutException
from starlette.websockets import WebSocketDisconnect

from app.general import redis_connection

from app.core.ai_utils import AIProcessingException
from app.core.translation import translate_text
from app.core.ai import getCaption, getDesign_Inspiration, getDesign_Information, getDesign_Meme, getDesign_Portrait, \
    getDesign_Promotion, getDesign_Quote, getDesign_News, getContentCategory, getIntent, getSubjectEntities, \
    getPostIdeas, get_post_ideas_v2_ai, getBio, getAdCopy, clip_prefix_caption_ai, clip_prefix_caption_ai_ws, \
    get_branddesc
from app.config import Settings

from app.core.ai import getSpellCheckFrench, getImprovedFormat, getEditCaption, getBR
from app.schemas import ImprovedFormatSchema, SpellCheckFrenchSchema, GetEditCaptionSchema, \
                            CaptionSchema, DesignSchema, CategorizerSchema, IntentAnalysisSchema, \
                            SubjectEntityAnalysisSchema, TranslateTextSchema, PostIdeasInputSchema, PostIdeasCategory, \
                            GetBioSchema, AdCopySchema, GetBrSchema, DESIGN_HELPER_DESCRIPTION

DEFAULT_BRAND_DESCRIPTION = "Lovevery delivers stage-based play, activity ideas, and development information for ages 0-3.\nOur play products and thoughtful guidance are created with child development experts to help you give your children the best possible start.\nLovevery.com"

LAST_TASK_ID_KEY = 'clip_prefix_caption_last_task_id'

social_manager_router = APIRouter()


@social_manager_router.get("/")
async def index():
    return Settings.PROJECT_NAME


@social_manager_router.post("/caption")
async def post_caption_helper(obj_in: CaptionSchema):
    logger.debug("started getting post_caption")
    brandInfo = obj_in.Initialisation
    postRequest = obj_in.postRequest
    lang = obj_in.postLanguage
    brandInfo_translated = []
    for i in range(len(brandInfo)):
        currentConcept = brandInfo[i].Concept
        currentCaption = brandInfo[i].Caption
        TranslatedConcept = translate_text(currentConcept, 'EN')
        TranslatedCaption = translate_text(currentCaption, 'EN')
        NewElement = {'Concept': TranslatedConcept, 'Caption': TranslatedCaption}
        brandInfo_translated.append(NewElement)
    postRequest_translated = translate_text(postRequest, 'EN')
    logger.debug("finished translate_text first stage")
    OutputCaption2 = getCaption(postRequest_translated, brandInfo_translated)
    logger.debug("finished getting post_caption")
    OutputCaption = OutputCaption2.replace('\nCaption:', '')
    OutputCaption_translated = translate_text(OutputCaption, lang)
    logger.debug("finished translate_text second stage")
    caption = {f'{lang} Caption': OutputCaption_translated, 'EN Caption': OutputCaption}
    return dumps(caption)


@social_manager_router.post("/design", description=DESIGN_HELPER_DESCRIPTION)
async def design_helper(obj_in: DesignSchema):
    category = obj_in.postCategory.lower()

    function_name = f'getDesign_{category.capitalize()}'
    postRequest = obj_in.postRequest
    postRequest_translated = translate_text(postRequest, 'EN')
    # logger.debug("postRequest_translated: " + postRequest_translated)
    OutputDesign = eval(function_name + '(postRequest_translated)')
    OutputDesign2 = OutputDesign.strip()
    Text = json.dumps(OutputDesign2).replace('\\n', ' , ').replace('\"', "")
    Dictionary = {i.split(': ')[0]: i.split(': ')[1] for i in Text.split(', ')}
    # logger.debug("Dictionary: " + str(Dictionary))
    lang = obj_in.postLanguage
    Dictionary["Image description"] = translate_text(Dictionary["Image description"], lang)
    Dictionary["Text to appear"] = translate_text(Dictionary["Text to appear"], lang)
    return json.dumps(Dictionary)


@social_manager_router.post("/categorizer")
async def content_categorizer(obj_in: CategorizerSchema):
    alt_text = obj_in.alt_text
    caption = obj_in.caption
    alt_text_english = translate_text(alt_text, 'EN')
    caption_english = translate_text(caption, 'EN')
    processed_category2 = getContentCategory(alt_text_english, caption_english)
    processed_category = processed_category2.strip()
    Text = json.dumps(processed_category).replace('\\n', ' , ').replace('\"', "")
    Dictionary = {i.split(': ')[0]: i.split(': ')[1] for i in Text.split(', ')}
    category = processed_category.replace('\nCategory:', '')
    return json.dumps(Dictionary)


@social_manager_router.get("/lang")
async def lang():
    return {
        'Bulgarian': 'BG',
        'Czech': 'CS',
        'Danish': 'DA',
        'German': 'DE',
        'Greek': 'EL',
        'English': 'EN',
        'Spanish': 'ES',
        'Estonian': 'ET',
        'Finnish': 'FI',
        'French': 'FR',
        'Hungarian': 'HU',
        'Italian': 'IT',
        'Japanese': 'JA',
        'Lithuanian': 'LT',
        'Latvian': 'LV',
        'Dutch': 'NL',
        'Polish': 'PL',
        'Portuguese': 'PT',
        'Romanian': 'RO',
        'Russian': 'RU',
        'Slovak': 'SK',
        'Slovenian': 'SL',
        'Swedish': 'SV',
        'Chinese': 'ZH'
    }


@social_manager_router.get("/cat")
async def cat():
    """
    Category can be : Inspiration, Promotion, Portrait, Quote, Meme, Information, News
    """
    return {
        '1': 'Information',
        '2': 'Promotion',
        '3': 'News',
        '4': 'Inspiration',
        '5': 'Portrait',
        '6': 'Quote',
        '7': 'Meme'
    }


@social_manager_router.get("/textTocat")
async def text_tocat():
    return {
        'Information about': 'Information',
        'Promoting': 'Promotion',
        'Portrait of': 'Portrait',
        'News about': 'News',
        'Quote about': 'Quote',
        'Inspirational quote about': 'Quote',
        'Fun fact about': 'Quote',
        'Fun quote about': 'Quote',
        'Funny meme about': 'Meme',
        'Funny picture about': 'Meme',
        "Inspiring people about": "Inspiration",
        "Inspiration about": "Inspiration"
    }


@social_manager_router.post("/intentAnalysis")
async def intent_analysis(obj_in: IntentAnalysisSchema):
    text = obj_in.text
    text_english = translate_text(text, 'EN')
    processed_intent2 = getIntent(text_english)
    processed_intent = processed_intent2.strip()
    Text = json.dumps(processed_intent).replace('\\n', ' , ').replace('\"', "")
    Dictionary = {i.split(': ')[0]: i.split(': ')[1] for i in Text.split(', ')}
    Intent = processed_intent.replace('\nIntent:', '')
    return json.dumps(Dictionary)
    # return 200


@social_manager_router.post("/subjectEntityAnalysis")
async def subject_entity_analysis(obj_in: SubjectEntityAnalysisSchema):
    text = obj_in.text
    text_english = translate_text(text, 'EN')
    processed_subject2 = getSubjectEntities(text_english)
    OutputSubjectEntity2 = processed_subject2.strip()
    Text = json.dumps(OutputSubjectEntity2).replace('\\n', ' , ').replace('\"', "")
    Dictionary = {i.split(': ')[0]: i.split(': ')[1] for i in Text.split(', ')}
    return json.dumps(Dictionary)


@social_manager_router.post("/translate")
async def translate(obj_in: TranslateTextSchema):
    text = obj_in.text
    output_lang = obj_in.output_lang
    return translate_text(text, output_lang)


@social_manager_router.post("/getPostIdeas")
async def get_post_ideas(obj_in: PostIdeasInputSchema):
    return getPostIdeas(obj_in.brand_type, obj_in.period)


OPENAI_ERRORS = (APIConnectionError, InvalidRequestError, APIError, TryAgain, Timeout, RateLimitError)
HTTPX_ERRORS = (ConnectTimeout, ReadTimeout, HTTPError, HTTPStatusError, RequestError, TimeoutException)


def exception_handler(e, exc_type: str = '', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY):
    message = f"Could not find post ideas: {exc_type} {type(e).__name__}, {e}"
    logger.exception(message + f", status_code:{status_code}", e)
    raise HTTPException(status_code=status_code, detail=message)


async def exception_dispatcher(function: callable, *args, **kwargs):
    try:
        res = function(*args, **kwargs)
        if isinstance(res, CoroutineType):
            return await res
        return res
    except AIProcessingException as e:
        exception_handler(e)
    except RateLimitError as e:
        exception_handler(e, 'OPENAI', status.HTTP_429_TOO_MANY_REQUESTS)
    except HTTPX_ERRORS as e:
        exception_handler(e, 'HTTPX')
    except OPENAI_ERRORS as e:
        exception_handler(e, 'OPENAI')


@social_manager_router.post("/getPostIdeas_v2")
async def get_post_ideas_v2(category: PostIdeasCategory, brand_type: str = "High-end cocktail bar",
                            period: int = Query(default=2, ge=1, le=12), context_string: str = '',
                            context_image: Optional[UploadFile] = File(None), context_image_url: Optional[str] = ''):
    res = exception_dispatcher(get_post_ideas_v2_ai, category, brand_type, period, context_string, context_image,
                               context_image_url)
    calculated_res = await res if isinstance(res, CoroutineType) else res
    return calculated_res


@social_manager_router.websocket("/getPostIdeas_v2_ws")
async def get_post_ideas_v2(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            response = {"response": None, "error": None}
            context_image = await websocket.receive_bytes()
            if context_image == b'\x00':
                logger.info("Ping")
                continue
            logger.debug("receive_bytes")
            json_object = await websocket.receive_json()
            logger.debug("receive_json")
            logger.info(json_object)
            calculated_res = None
            try:
                category = PostIdeasCategory(json_object['category'])
                brand_type = json_object['brand_type']
                period = json_object['period']
                if not (1 <= period <= 12):
                    raise ValueError('Period not in range')
                context_string = json_object['context_string']
                res = exception_dispatcher(get_post_ideas_v2_ai, category, brand_type, period, context_string,
                                           None, context_image)
                response['response'] = await res if isinstance(res, CoroutineType) else res
                response_str = dumps(response)
            except (ValueError, KeyError) as e:
                response['error'] = str(e)
                response_str = dumps(response)
                await websocket.send_text(response_str)
                continue
            except Exception as e:
                response['error'] = str(e)
                response_str = dumps(response)
                await websocket.send_text(response_str)
                raise e
            response_str = dumps(response)
            await websocket.send_text(response_str)
    except WebSocketDisconnect:
        logger.info("websocket disconnected")
    except Exception as e:
        try:
            response = {'response': None, 'error': str(e)}
            response_str = dumps(response)
            await websocket.send_text(response_str)
        except WebSocketDisconnect:
            logger.error("websocket disconnected on hadling exception")
        raise e


class Status(StrEnum):
    enqueued = 'enqueued'
    busy = 'busy'
    completed = 'completed'
    # wrong_format = 'wrong_format'  # not used, can be added if needed


async def clip_prefix_caption_background_task(picture: UploadFile, task_id: int):
    task_info = dumps({'result': '', 'status': Status.busy})
    if not redis_connection.set(task_id, task_info):
        logger.error(f"Could not set task info:{task_info} for task_id: {task_id} in Redis")
    try:
        logger.info(f"started, task_id:{task_id}",
                    f"picture:{picture.filename}")
        start = time.time()

        res = clip_prefix_caption_ai(picture)
        calculated_res = await res if isinstance(res, CoroutineType) else res

        end = time.time()

        task_info = dumps({'result': calculated_res, 'status': Status.completed})
        if not redis_connection.set(task_id, task_info):
            logger.error(f"Could not add result for task_id:{task_id} in Redis")
        else:
            logger.info(f"task_id:{task_id} completed, time taken: {end - start:.4f}")
    except Exception as e:  # add retry for failed tasks for OpenAI and HTTPX errors
        logger.exception(f"task_id:{task_id}", e)
        raise e


@social_manager_router.post("/clip_prefix_caption_upload")
async def clip_prefix_caption_upload(background_tasks: BackgroundTasks, picture: UploadFile = File(...)):
    task_id = redis_connection.incr(LAST_TASK_ID_KEY)

    task_info = redis_connection.get(task_id)
    if task_info is None:  # case when task_id is not created
        task_info = dumps({'result': '', 'status': Status.enqueued})
        if not redis_connection.set(task_id, task_info):
            logger.error(f"Could not set task info:{task_info} for task_id: {task_id} in Redis")
        background_tasks.add_task(clip_prefix_caption_background_task, picture, task_id)
        logger.info(f"image: {picture.filename}, task_id: {task_id}, started")
        return JSONResponse({"task_id": task_id, "status": Status.completed})
    else:
        detail = f"task_id:{task_id} already exists in Redis, try again"
        logger.error(detail + f", {task_info}, {redis_connection.keys()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=detail)


@social_manager_router.post("/clip_prefix_caption_result")
async def clip_prefix_caption_result(task_id: int):
    result = redis_connection.get(task_id)
    if result is None:
        return HTMLResponse(content="Task wasn't created", status_code=404)
    else:
        result = loads(result)
        if result['status'] == Status.busy:
            return JSONResponse({"task_id": task_id, "status": Status.busy})
        elif result['status'] == Status.completed:
            if not redis_connection.delete(task_id):
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail=f"Could not delete task_id:{task_id} in Redis")
            else:
                logger.info(f"task_id:{task_id} deleted from Redis")
            return JSONResponse({"task_id": task_id, "status": Status.completed, "result": result['result']})
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"task_id:{task_id} has wrong status:{result['status']} in Redis")


@social_manager_router.websocket("/clip_prefix_caption_ws")
async def clip_prefix_caption_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            logger.info('-------')
            image = await websocket.receive_bytes()
            if image == b'\x00':
                logger.info("Ping")
                continue
            caption = await clip_prefix_caption_ai_ws(image)
            await websocket.send_text(caption)
    except WebSocketDisconnect as e:
        logger.info("websocket disconnected")


@social_manager_router.post("/clip_prefix_caption")
async def clip_prefix_caption(image: UploadFile = File(...)):
    res = exception_dispatcher(clip_prefix_caption_ai, image)
    calculated_res = await res if isinstance(res, CoroutineType) else res
    return calculated_res


@social_manager_router.post("/getBio")
async def get_bio(obj_in: GetBioSchema):
    return getBio(obj_in.brand_name, obj_in.brand_type, obj_in.brand_objective)


@social_manager_router.post('/improved_format')
async def improved_format(obj_in: ImprovedFormatSchema):
    # Improve format of the text
    result = getImprovedFormat(obj_in.text)
    return result


@social_manager_router.post('/spell_check_french')
async def spell_check_french(obj_in: SpellCheckFrenchSchema):
    # Spell check French
    result = getSpellCheckFrench(obj_in.text)
    return result


@social_manager_router.post('/edit_caption')
async def edit_caption(obj_in: GetEditCaptionSchema):
    # Edit Caption
    result = getEditCaption(obj_in.caption, obj_in.edit)
    return result


@social_manager_router.post("/Adcopy")
async def post_adcopy_helper(obj_in: AdCopySchema):
    competitorInfo = obj_in.Initialisation
    inputCTA = obj_in.CTA
    inputBrandDesc = obj_in.BrandDesc
    inputKeyfeature = obj_in.Keyfeature
    inputAudience = obj_in.Audience
    inputBrandName = obj_in.BrandName
    lang = obj_in.copyLanguage
    competitorInfo_translated = []
    brief_desc = " for a "
    brief_kf = " that offers "
    brief_audience = " targeting "
    brief_name = " named "
    for i in range(len(competitorInfo)):
        competitorCTA = competitorInfo[i]["CTA"]
        competitorBrandDesc = competitorInfo[i]["BrandDesc"]
        competitorKeyfeature = competitorInfo[i]["Keyfeature"]
        competitorAudience = competitorInfo[i]["Audience"]
        competitorBrandName = competitorInfo[i]["BrandName"]
        competitorHeadline = competitorInfo[i]["Headline"]
        competitorDescription = competitorInfo[i]["Description"]
        competitorPrimary = competitorInfo[i]["Primary"]
        TranslatedCTA = translate_text(competitorCTA, 'EN')
        TranslatedBrandDesc = translate_text(competitorBrandDesc, 'EN')
        TranslatedKeyfeature = translate_text(competitorKeyfeature, 'EN')
        TranslatedAudience = translate_text(competitorAudience, 'EN')
        TranslatedBrief = f'{TranslatedCTA}{brief_desc}{TranslatedBrandDesc}{brief_kf}{TranslatedKeyfeature}{brief_audience}{TranslatedAudience}{brief_name}{competitorBrandName}'
        TranslatedHeadline = translate_text(competitorHeadline, 'EN')
        TranslatedDescription = translate_text(competitorDescription, 'EN')
        TranslatedPrimary = translate_text(competitorPrimary, 'EN')
        NewElement = {'Brief': TranslatedBrief, 'Headline': TranslatedHeadline, 'Description': TranslatedDescription,
                      'Primary': TranslatedPrimary}
        competitorInfo_translated.append(NewElement)

    inputCTA_translated = translate_text(inputCTA, 'EN')
    inputBrandDesc_translated = translate_text(inputBrandDesc, 'EN')
    inputKeyfeature_translated = translate_text(inputKeyfeature, 'EN')
    inputAudience_translated = translate_text(inputAudience, 'EN')

    OutputAdCopy = getAdCopy(inputCTA_translated, inputBrandDesc_translated, inputKeyfeature_translated,
                             inputAudience_translated, inputBrandName, competitorInfo_translated)

    output_list = OutputAdCopy.replace("Ad Headline:", "|").replace("Ad Description:", "|").replace("Ad Primary Text:", "|")
    output_list = output_list.replace("\n\n", "\n").replace("\n", "")

    output_list = output_list.split("|")

    output_list = [o for o in output_list if o != ""]

    OutputHeadline = output_list[-3]
    OutputDescription = output_list[-2]
    OutputPrimary = output_list[-1]

    OutputHeadline_translated = translate_text(OutputHeadline, lang)
    OutputDescription_translated = translate_text(OutputDescription, lang)
    OutputPrimary_translated = translate_text(OutputPrimary, lang)

    text = dumps(
        {f'{lang} Ad Headline': OutputHeadline_translated, f'{lang} Ad Description': OutputDescription_translated,
         f'{lang} Ad Primary Text': OutputPrimary_translated, 'EN Ad Headline': OutputHeadline,
         'EN Ad Description': OutputDescription, 'EN Ad Primary Text': OutputPrimary})
    return text


@social_manager_router.post('/getBr')
async def get_br(obj_in: GetBrSchema):
    # Edit Caption
    result = getBR(obj_in.description, obj_in.user_story)
    return result


@social_manager_router.post('/get_brand_description')
async def get_brand_description(description: str = DEFAULT_BRAND_DESCRIPTION):
    result = get_branddesc(description)
    return result
