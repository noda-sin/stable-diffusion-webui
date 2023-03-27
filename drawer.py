import time
import requests
import remote_config
import random
from PIL import Image
from io import BytesIO
import base64
import traceback
import threading

from chat_gpt import ChatGTP
from slack import Slack
from logger import logger

def rand_lora():
    jp = random.random()
    kr = random.random()
    tj = random.random()
    sum = jp + kr + tj
    jp = jp / sum * 0.3
    kr = kr / sum * 0.3
    tj = tj / sum * 0.3
    return f"<lora:japaneseDollLikeness_v10:{jp}>,<lora:koreanDollLikeness_v15:{kr}>,<lora:taiwanDollLikeness_v10:{tj}>,"


class Drawer(object):
    def __init__(self):
        self.slack = Slack()
        self.chat_gpt = ChatGTP()


    def _draw(self):
        # 1. Create peramters
        prompt = self.chat_gpt.get_params()
        quote = self.chat_gpt.get_quote(prompt)        
        params = remote_config.config().copy()
        params["prompt"] = params["prompt"] + f"{rand_lora()}(({prompt}))"
        params["seed"] = random.randint(1, 1999999999)

        # 2. Draw
        resp = requests.post(url="http://127.0.0.1:7860/sdapi/v1/txt2img", json=params)
        resp.raise_for_status()

        json = resp.json()
        images = [
            Image.open(BytesIO(base64.b64decode(image))) for image in json['images']
        ]

        # 1. Send image with quote
        thread_ts = self.slack.send_image(images[0], text=quote)

        # 2. Send parameters
        self.slack.send_message(f"""
prompt: {params['prompt']}
seed: {json['parameters']['seed']}
""", thread_ts=thread_ts)

        # 3. Send left images
        for image in images[1:]:
            self.slack.send_image(image, thread_ts=thread_ts)


    def __run(self):
        while self.running:
            try:
                self._draw()
            except Exception as e:
                logger.error(traceback.format_exc())
            time.sleep(10)


    def start(self):
        try:
            self.running = True
            threading.Thread(target=self.__run).start()
            logger.info("Drawer is running!")
            self.slack.start()
        finally:
            self.running = False
