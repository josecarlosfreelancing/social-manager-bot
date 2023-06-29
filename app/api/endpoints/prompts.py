from fastapi import APIRouter, status, HTTPException, Query
from fastapi.responses import JSONResponse
from openai.error import APIConnectionError, InvalidRequestError, APIError, TryAgain, Timeout, RateLimitError

from app.core.ai import getprompt_food, getprompt_portrait, getprompt_object, getprompt_icon, getprompt_scene, getprompt_illustration, getprompt_render, getprompt_action, getimage
from app.schemas import PromptsCategory

prompts_router = APIRouter()


# case statement for each prompt category
def get_prompt_function(prompt: PromptsCategory):
    switcher = {
        PromptsCategory.food: getprompt_food,
        PromptsCategory.portrait: getprompt_portrait,
        PromptsCategory.object: getprompt_object,
        PromptsCategory.icon: getprompt_icon,
        PromptsCategory.scene: getprompt_scene,
        PromptsCategory.illustration: getprompt_illustration,
        PromptsCategory.render: getprompt_render,
        PromptsCategory.action: getprompt_action
    }
    return switcher.get(prompt, "Invalid prompt category")


@prompts_router.post("/prompts/")
async def get_prompts(category: PromptsCategory = PromptsCategory.food,
                      description: str = "A picture of a bread",
                      number_of_images: int = Query(default=1, ge=1, le=10)):
    # prompt = GetPromptSchema(category=category, description=description, number_of_images=number_of_images)
    """Categories can be:
    food, portrait, object, icon, scene, illustration, render, action"""
    try:
        prompt_function = get_prompt_function(category)
        prompt_text = prompt_function(description)
        image_urls = getimage(prompt_text, number_of_images)
        return JSONResponse(image_urls)
    except APIConnectionError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Could not get prompts: {}".format(e))
    except InvalidRequestError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Could not get prompts: {}".format(e))
    except APIError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Could not get prompts: {}".format(e))
    except TryAgain as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Could not get prompts: {}".format(e))
    except Timeout as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Could not get prompts: {}".format(e))
    except RateLimitError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Could not get prompts: {}".format(e))
