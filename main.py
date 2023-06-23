# pip install -q google-generativeai
from db.db import bot_token, signing_secret, app_token
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import re
from translator.translator import text_to_eng, text_to_kor
from ai.palm import PALM_BOT

app = App(token=bot_token, signing_secret=signing_secret)
client = WebClient(token=bot_token)


def send_message(channel, text, thread_ts=None):
    try:
        response = client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)
        return response
    except SlackApiError as e:
        text = f"Error sending message: {e.response['error']}"
        client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)


def processing_prompt(prompt):
    def split_text(text):
        pattern = r"```[\s\S]*?```"  # 백틱으로 된 코드 블록을 찾는 정규식 패턴
        code_blocks = re.findall(pattern, text)
        sentences = re.split(pattern, text)

        return sentences, code_blocks

    def listToString(str_list):
        result = ""
        for s in str_list:
            result += s + " "
        return result.strip()

    generated_text = PALM_BOT.generate_text(text_to_eng(prompt))

    sentences, code_blocks = split_text(generated_text)
    kor_sentences = []
    for sentence in sentences:
        text_to_korean = text_to_kor(sentence)
        kor_sentences.append(text_to_korean)
    merged_list = [
        kor_sentence + code_block for kor_sentence, code_block in zip(kor_sentences, code_blocks)
    ]
    result = listToString(merged_list)
    return result


@app.event("message")
def handle_message_event(event):
    channel_type = event["channel_type"]
    text = event["text"]
    ts = event["ts"]
    channel = event["channel"]
    # DM 이벤트인지 확인
    if channel_type == "im":
        prompt = processing_prompt(text)
        send_message(channel=channel, text=prompt, thread_ts=ts)
        # client.chat_postMessage(channel=channel, text=prompt, thread_ts=ts)


@app.event("app_mention")
def handle_mention(body, say, logger, event):
    pattern = r"<@[\w\d]+>"
    text = re.sub(pattern, "", event["text"]).strip()
    ts = event["ts"]
    channel = event["channel"]
    prompt = processing_prompt(text)
    send_message(channel=channel, text=prompt, thread_ts=ts)


if __name__ == "__main__":
    # Start the bot
    handler = SocketModeHandler(app_token=app_token, app=app)
    handler.start()
