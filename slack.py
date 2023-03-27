import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from PIL import Image
import io
import uuid
import traceback
import random

from logger import logger
from draw_queue import DrawQueue

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
queue = DrawQueue()


def get_message(channel, ts):
    res = app.client.conversations_replies(channel=channel, ts=ts)
    for message in res['messages']:
        if message['ts'] == ts:
            return message
    return None


def parse_job_from_message(message):
    if not "prompt / " in message:
        return None

    prompt = None
    seed = None

    for line in message.splitlines():
        if len(line.split('/')) != 2:
            continue
        key, value = line.split('/')
        if key.strip() == 'prompt':
            prompt = value
        if key.strip() == 'seed':
            seed = int(value)
    return {
        'prompt': prompt,
        'seed': seed,
        'enable_hr': False,
    }


def enqueue(job, thread_ts):
    job['thread_ts'] = thread_ts
    queue.push(job)


@app.event("message")
def handle_message(body, say):
    event = body['event']

    if event['user'] != 'U04TDUX13BK':
        return

    thread_ts = event['event_ts']
    message = event['text']

    job = parse_job_from_message(message)
    if job:
        enqueue(job, thread_ts)
        say("Enque draw request", thread_ts=thread_ts)


@app.event("reaction_added")
def handle_reaction(body, say):
    event = body['event']
    
    if event['user'] != 'U04TDUX13BK':
        return
    
    reaction = event['reaction']
    channel = event['item']['channel']
    ts = event['item']['ts']
    message = get_message(channel, ts)
    message_text = message['text']
    thread_ts = message['thread_ts']

    if reaction == 'gacha':
        job = parse_job_from_message(message_text)
        job['seed'] = random.randint(1, 1999999999)
        enqueue(job, thread_ts)
        say("Enque :gacha: request", thread_ts=thread_ts)
    elif reaction == 'plus':
        job = parse_job_from_message(message_text)
        job['seed'] = job['seed'] + 1
        enqueue(job, thread_ts)
        say("Enque :plus: request", thread_ts=thread_ts)
    elif reaction == 'bai':
        job = parse_job_from_message(message_text)
        job['enable_hr'] = True
        enqueue(job, thread_ts)
        say("Enque :bai: request", thread_ts=thread_ts)


class Slack(object):
    def __init__(self):
        self.client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        self.channel = "##stable-diffusion"


    def send_message(self, text: str, thread_ts=None):
        try:
            resp = self.client.chat_postMessage(channel=self.channel, text=text, thread_ts=thread_ts)
            return resp["ts"]
        except Exception as e:
            print(f"Fail to send text: {e}")
            print(traceback.format_exc())


    def send_image(self, img: Image, text=None, thread_ts=None):
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        try:
            resp = self.client.files_upload(channels=[self.channel], thread_ts=thread_ts, filename=f"{uuid.uuid4()}.png", file=img_bytes.getvalue(),
                                            initial_comment=text)
            for channel in resp["file"]["shares"]["public"].values():
                return channel[0]['ts']
        except Exception as e:
            print(f"Fail to send image: {e}")
            print(traceback.format_exc())


    def start(self):
        SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
