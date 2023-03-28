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
from chat_gpt import ChatGPT

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
queue = DrawQueue()
chat_gpt = ChatGPT()


def get_prev_job(channel, ts):
    res = app.client.conversations_replies(channel=channel, ts=ts)
    messages = res['messages']
    messages.reverse()
    for message in messages:
        text = message['text']
        job = parse_job_from_message(text)
        if job:
            return job
    return None


def get_message(channel, ts):
    res = app.client.conversations_replies(channel=channel, ts=ts)
    for message in res['messages']:
        if message['ts'] == ts:
            return message
    return None


def parse_job_from_message(message):
    if not message:
        return None

    if not "prompt / " in message:
        return None

    params = {}
    for line in message.splitlines():
        if len(line.split('/')) != 2:
            continue
        key, value = line.split('/')
        params[key.strip()] = value.strip()
    return params


def enqueue(job, thread_ts=None):
    job['thread_ts'] = thread_ts
    queue.push(job)


@app.event("message")
def handle_message(body, say):
    event = body['event']
    logger.info(f"Recieved message event: {event}")

    if event['user'] != 'U04TDUX13BK':
        return

    channel = event['channel']
    message = event['text']
    if 'thread_ts' in event:
        thread_ts = event['thread_ts']
        prev_job = get_prev_job(channel, thread_ts)
        logger.info(f"prev job: {prev_job}")
        if prev_job:
            prev_prompt = prev_job['prompt']
            next_prompt = chat_gpt.get_next_params(prev_prompt, message)
            job = prev_job.copy()
            job['prompt'] = next_prompt
            enqueue(job, thread_ts)
            say(f"Enqeue improve request / {next_prompt}", thread_ts=thread_ts)
    else:
        job = parse_job_from_message(message)
        if job:
            enqueue(job)
            say("Enqeue draw request", thread_ts=event['event_ts'])


@app.event("reaction_added")
def handle_reaction(body, say):
    event = body['event']
    logger.info(f"Recieved reaction event: {event}")

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
    if reaction == '10_gacha':
        for _ in range(10):
            job = parse_job_from_message(message_text)
            job['seed'] = random.randint(1, 1999999999)
            enqueue(job, thread_ts)
        say("Enqeue :10_gacha: request", thread_ts=thread_ts)
    elif reaction == 'plus':
        job = parse_job_from_message(message_text)
        job['seed'] = job['seed'] + 1
        enqueue(job, thread_ts)
        say("Enqeue :plus: request", thread_ts=thread_ts)
    elif reaction == 'bai':
        job = parse_job_from_message(message_text)
        job['enable_hr'] = True
        enqueue(job, thread_ts)
        say("Enqeue :bai: request", thread_ts=thread_ts)


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
