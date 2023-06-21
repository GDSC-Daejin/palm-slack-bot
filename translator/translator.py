import requests
import uuid
from db.db import azure_api_key

print(azure_api_key)


def text_to_eng(text):
    # Azure Cognitive Services 리소스에서 얻은 엔드포인트 및 구독 키
    key = azure_api_key

    # 번역할 텍스트
    text_to_translate = text

    # 번역 요청 URL
    url = f"https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=en"

    # 번역 요청 헤더 및 본문 데이터
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }
    data = [{"text": text_to_translate}]

    # 번역 요청 보내기
    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    # 번역 결과 확인
    translated_text = result[0]["translations"][0]["text"]
    return translated_text
