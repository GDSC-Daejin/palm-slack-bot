# pip install -q google-generativeai
from db import get_api_key
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from palm import PalmBot
import re
import json
import requests
import uuid

api_key = get_api_key()
app_token = api_key["PALM_SLACK_APP_TOKEN"]
bot_token = api_key["PALM_SLACK_BOT_TOKEN"]
signing_secret = api_key["PALM_SLACK_SIGNING_SECRET"]
palm_token = api_key["WS_PALM_API_KEY"]
azure_translate_api = api_key["AZURE_TRANSLATOR_API"]

app = App(token=bot_token, signing_secret=signing_secret)
bot = PalmBot(palm_token)
client = WebClient(token=bot_token)


def send_markdown_message(channel, text, thread_ts=None):
    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": text}}]

    try:
        response = client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)
        return response
    except SlackApiError as e:
        text = f"Error sending message: {e.response['error']}"
        client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)


def text_to_eng(text):
    # Azure Cognitive Services 리소스에서 얻은 엔드포인트 및 구독 키
    key = azure_translate_api

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


def text_to_kor(text):
    text = text_to_eng(text)
    prompt = bot.generate_text(text + " in korean")
    return prompt


@app.command("/palm")
def repeat_text(ack, respond, command, say, body):
    ack()
    prompt = bot.generate_text(f"{command['text']}")
    prompt = text_to_kor(prompt)
    say(prompt)


@app.event("message")
def handle_message_event(event):
    channel_type = event["channel_type"]
    text = event["text"]
    ts = event["ts"]
    channel = event["channel"]
    # DM 이벤트인지 확인
    if channel_type == "im":
        prompt = text_to_kor(text)
        send_markdown_message(channel=channel, text=prompt, thread_ts=ts)
        # client.chat_postMessage(channel=channel, text=prompt, thread_ts=ts)


@app.event("app_mention")
def handle_mention(body, say, logger, event):
    pattern = r"<@[\w\d]+>"
    text = re.sub(pattern, "", event["text"]).strip()
    prompt = text_to_kor(text)
    ts = event["ts"]
    channel = event["channel"]
    send_markdown_message(channel=channel, text=prompt, thread_ts=ts)


if __name__ == "__main__":
    # Start the bot
    handler = SocketModeHandler(app_token=app_token, app=app)
    handler.start()
