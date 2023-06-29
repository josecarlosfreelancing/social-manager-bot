import os

import openai
from fastapi import status


class AIProcessingException(Exception):
    @staticmethod
    def http_status():
        return status.HTTP_422_UNPROCESSABLE_ENTITY


def get_open_ai_completion() -> openai.Completion:
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    completion = openai.Completion()
    return completion
