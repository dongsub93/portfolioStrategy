import ctypes
import win32com.client
from datetime import datetime
import requests
import json
import os




path = os.path.dirname(os.path.abspath(__file__))
with open(path+'/../env.json', 'r') as f:
    config = json.load(f)

token = config['private']["token"]
channel = config['private']["channel"]



def post_message(message):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Content-Type":"application/json", "Authorization": "Bearer "+token},
        data=json.dumps({"channel": channel,"text": message})
    )

def send_slack_chat(message):
    print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message)
    strbuf = datetime.now().strftime('[%m/%d %H:%M:%S] ') + message
    post_message(strbuf)


def print_log(message, *args):
    print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message, *args)

