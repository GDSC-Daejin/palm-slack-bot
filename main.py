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


def send_message(channel, eng, kor, thread_ts=None):
    try:
        response = client.chat_postMessage(channel=channel, text=kor, thread_ts=thread_ts)
        return response
    except SlackApiError as e:
        print(text, e)
        text = f"Error sending message: {e.response['error']}"
        response = client.chat_postMessage(channel=channel, text=eng, thread_ts=thread_ts)


def processing_prompt(prompt):
    result = ""

    def split_text(text):
        pattern = r"```[\s\S]*?```"  # Regular expression pattern to find code blocks enclosed in backticks
        code_blocks = re.findall(pattern, text)
        sentences = re.split(pattern, text)
        return sentences, code_blocks

    def list_to_string(str_list):
        return " ".join(str_list).strip()

    eng_result = PALM_BOT.generate_text(text_to_eng(prompt))

    if isinstance(eng_result, dict):
        eng_result = str(eng_result)
        return eng_result, eng_result
    else:
        sentences, code_blocks = split_text(eng_result)
        kor_sentences = [text_to_kor(sentence) for sentence in sentences]

        merged_list = []
        for i, kor_sentence in enumerate(kor_sentences):
            if i < len(code_blocks):
                merged_list.append(kor_sentence + code_blocks[i])
            else:
                # Handling the case where there are more kor_sentences than code_blocks
                merged_list.append(kor_sentence)

        kor_result = list_to_string(merged_list)
        return eng_result, kor_result


@app.event("message")
def handle_message_event(event):
    channel_type = event["channel_type"]
    text = event["text"]
    ts = event["ts"]
    channel = event["channel"]
    # DM 이벤트인지 확인
    if channel_type == "im":
        eng, kor = processing_prompt(text)
        send_message(channel=channel, eng=eng, kor=kor, thread_ts=ts)
        # client.chat_postMessage(channel=channel, text=prompt, thread_ts=ts)


@app.event("app_mention")
def handle_mention(body, say, logger, event):
    pattern = r"<@[\w\d]+>"
    text = re.sub(pattern, "", event["text"]).strip()
    ts = event["ts"]
    channel = event["channel"]
    eng, kor = processing_prompt(text)
    send_message(channel=channel, eng=eng, kor=kor, thread_ts=ts)


if __name__ == "__main__":
    # Start the bot
    handler = SocketModeHandler(app_token=app_token, app=app)
    handler.start()
