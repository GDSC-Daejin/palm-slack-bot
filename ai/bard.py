from bardapi import Bard
import os
import requests
from db.db import bard_api_key


sessions = {}


def get_answer_from_bard(thread_id, prompt):
    try:
        print(thread_id)
        if thread_id not in sessions:
            session = requests.Session()
            print(session)
            session.headers = {
                "Host": "bard.google.com",
                "X-Same-Domain": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Origin": "https://bard.google.com",
                "Referer": "https://bard.google.com/",
            }
            session.cookies.set("__Secure-1PSID", bard_api_key)
            bard = Bard(token=bard_api_key, session=session, timeout=30)
            sessions[thread_id] = bard
        else:
            bard = sessions[thread_id]
        result = f""" 바드 : {bard.get_answer(prompt)["content"]}"""
        return result
    except Exception as e:
        print(e)
        pass
