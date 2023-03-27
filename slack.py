import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from PIL import Image
import io
import uuid
import traceback


app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


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


    def send_image(self, img: Image, thread_ts=None):
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        try:
            self.client.files_upload(channels=[self.channel], thread_ts=thread_ts, filename=f"{uuid.uuid4()}.png", file=img_bytes.getvalue())
        except Exception as e:
            print(f"Fail to send image: {e}")
            print(traceback.format_exc())


    @app.message("hello")
    def message_hello(message, say):
        say(f"Hey there <@{message['user']}>!")


    def start(self):
        SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
