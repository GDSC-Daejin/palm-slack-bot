import pprint
import google.generativeai as palm
import sys
from db.db import palm_api_key
import re


class PALM:
    def __init__(self, api_key):
        palm.configure(api_key=api_key)
        self.models = [
            m for m in palm.list_models() if "generateText" in m.supported_generation_methods
        ]
        self.model = self.models[0].name

    def generate_text(self, prompt):
        try:
            completion = palm.generate_text(
                model=self.model,
                prompt=prompt,
                temperature=1.0,
                max_output_tokens=self.models[0].output_token_limit,
            )
            if completion.result is None:
                completion = completion.filters[0]
            else:
                completion = completion.result

        except Exception as e:
            print(e)
            completion = "영어, palm이 대답하기 싫은거 입력했어요."

        return completion


PALM_BOT = PALM(palm_api_key)
