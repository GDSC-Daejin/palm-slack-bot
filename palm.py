import pprint
import google.generativeai as palm


class PalmBot:
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
                temperature=0,
                max_output_tokens=self.models[0].output_token_limit,
            )
            completion = completion.result
        except Exception as e:
            completion = "아 영어로만 쓰라구 ㅋㅋ"
        return completion
