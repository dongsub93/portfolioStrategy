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



def postMessage(message):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Content-Type":"application/json", "Authorization": "Bearer "+token},
        data=json.dumps({"channel": channel,"text": message})
    )

def sendSlackChat(message):
    print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message)
    strbuf = datetime.now().strftime('[%m/%d %H:%M:%S] ') + message
    postMessage(strbuf)


def printlog(message, *args):
    print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message, *args)

