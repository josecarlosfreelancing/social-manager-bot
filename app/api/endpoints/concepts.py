from fastapi import APIRouter, status, HTTPException, Query
from fastapi.responses import JSONResponse
from openai.error import APIConnectionError, InvalidRequestError, APIError, TryAgain, Timeout, RateLimitError

from app.core.ai_concepts import get_concept_function
from app.schemas import ConceptCategory, CONCEPTS_HELPER_DESCRIPTION

concepts_router = APIRouter()


@concepts_router.post("/concepts/", description=CONCEPTS_HELPER_DESCRIPTION)
async def get_concepts(description: str, month: str, category: ConceptCategory = ConceptCategory.information):
    try:
        concept_function = get_concept_function(category)
        if concept_function is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid concept category")
        concept_text = concept_function(description, month)
        return concept_text  # JSONResponse(image_urls)
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
