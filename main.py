# pip install -q google-generativeai
from datetime import datetime
from db.db import bot_token, signing_secret, app_token
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import re
from translator.translator import *
from ai.palm import PALM_BOT


app = App(token=bot_token, signing_secret=signing_secret)
client = WebClient(token=bot_token)


def mention_add(channel, ts):
    client.reactions_add(name="spinner", channel=channel, timestamp=ts)


def mention_reomove(channel, ts):
    client.reactions_remove(name="spinner", channel=channel, timestamp=ts)


def send_message(channel, eng, kor, bard=None, thread_ts=None):
    try:
        client.chat_postMessage(channel=channel, text=kor, thread_ts=thread_ts)

    except SlackApiError as e:
        # print(text, e)
        # text = f"Error sending message: {e.response['error']}"
        client.chat_postMessage(channel=channel, text=eng, thread_ts=thread_ts)


def processing_prompt(prompt, channel, ts):
    result = ""
    record_log(channel=channel, tx=prompt)
    mention_add(channel, ts)

    def split_text(text):
        pattern = r"```[\s\S]*?```"  # Regular expression pattern to find code blocks enclosed in backticks
        code_blocks = re.findall(pattern, text)
        sentences = re.split(pattern, text)
        return sentences, code_blocks

    def list_to_string(str_list):
        return " ".join(str_list).strip()

    prompt = translate_kor_to_eng(prompt)

    eng_result = PALM_BOT.generate_text(prompt)
    if isinstance(eng_result, dict):
        eng_result = str(eng_result)
        mention_reomove(channel, ts)
        return eng_result, eng_result
    else:
        sentences, code_blocks = split_text(eng_result)
        kor_sentences = [translate_eng_to_kor(sentence) for sentence in sentences]

        merged_list = []
        for i, kor_sentence in enumerate(kor_sentences):
            if i < len(code_blocks):
                merged_list.append(kor_sentence + "\n\n" + code_blocks[i])
            else:
                # Handling the case where there are more kor_sentences than code_blocks
                merged_list.append(kor_sentence)

        kor_result = list_to_string(merged_list)
        mention_reomove(channel, ts)
        return eng_result, kor_result


def record_log(channel, channel_type=None, tx=None, eng, kor):
    now = datetime.now()
    if channel_type:
        print(str(now) + f" {channel_type} :  " + tx)
        print(str(now) + f" 영어 :  " + eng)
        print(str(now) + f" 한글 :  " + kor)
        return
    else:
        print(str(now) + f"  {channel}  :  {tx}")
        print(str(now) + f" 영어 :  " + eng)
        print(str(now) + f" 한글 :  " + kor)
        
        return


@app.event("message")
def handle_message_event(event, message, say):
    channel_type = event["channel_type"]
    text = event["text"]
    ts = event["ts"]
    channel = event["channel"]
    # DM 이벤트인지 확인

    if channel_type == "im":
        
        eng, kor = processing_prompt(text, channel=channel, ts=ts)
        record_log(channel=channel, channel_type=channel_type, tx=text,eng=eng,kor=kor)
        send_message(channel=channel, eng=eng, kor=kor, thread_ts=ts)
        # client.chat_postMessage(channel=channel, text=prompt, thread_ts=ts)


@app.event("app_mention")
def handle_mention(body, say, logger, event, message):
    pattern = r"<@[\w\d]+>"
    text = re.sub(pattern, "", event["text"]).strip()
    ts = event["ts"]
    channel = event["channel"]
    eng, kor = processing_prompt(text, channel=channel, ts=ts)
    # bard = get_answer_from_bard(ts, text)
    record_log(channel=channel, tx=text,eng=eng,kor=kor)
    send_message(channel=channel, eng=eng, kor=kor, thread_ts=ts)


if __name__ == "__main__":
    # Start the bot
    handler = SocketModeHandler(app_token=app_token, app=app)
    handler.start()
