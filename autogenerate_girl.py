import subprocess
import time
import requests
from chat_gpt import ChatGTP
import remote_config
import sys
import argparse
from slack_sdk import WebClient
import uuid
import random
import io
from PIL import Image
from io import BytesIO
import base64
import traceback

def is_launched():
    try:
        r = requests.get('http://127.0.0.1:7860/robots.txt')
        return r.status_code == 200
    except:
        return False


def wait_for_launch():
    while not is_launched():
        time.sleep(1)

def generate_girl_txt(gpt_token):
    print("start to generate txt by chatGPT")
    txt = chat_gpt.generate_girl_params(gpt_token)
    while txt is None:
        time.sleep(10)
        txt = chat_gpt.generate_girl_params(gpt_token)
    print(f"generated txt by chatGPT: {txt}")
    return txt

def lora():
    jp = random.random()
    kr = random.random()
    tj = random.random()
    sum = jp + kr + tj
    jp = jp / sum * 0.3
    kr = kr / sum * 0.3
    tj = tj / sum * 0.3
    return f"<lora:japaneseDollLikeness_v10:{jp}>,<lora:koreanDollLikeness_v15:{kr}>,<lora:taiwanDollLikeness_v10:{tj}>,"


def send_txt(token, channel, text: str, thread_ts=None):
    client = WebClient(token=token)
    try:
        resp = client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)
        return resp["ts"]
    except Exception as e:
        print(f"Fail to send text: {e}")


def send_img(token, channel, img: Image, thread_ts):
    if not token:
        return

    client = WebClient(token=token)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    try:
        client.files_upload(channels=[channel], thread_ts=thread_ts, filename=f"{uuid.uuid4()}.png", file=img_bytes.getvalue())
    except Exception as e:
        print(f"Fail to send image: {e}")


def generate_girl(chat_gpt: ChatGTP, slack_token, slack_channel):
    try:
        txt = chat_gpt.get_params()
        quote = chat_gpt.get_quote(txt)
        params = remote_config.config().copy()
        params["prompt"] = params["prompt"] + f"{lora()}(({txt}))"
        print("Start to generate girl", params)
        resp = requests.post(url="http://127.0.0.1:7860/sdapi/v1/txt2img", json=params)
        if resp.status_code == 200:
            print(f"Success to generate girl: {txt}")
            thread_ts = send_txt(slack_token, slack_channel, quote)
            send_txt(slack_token, slack_channel, f"{params['prompt']}/{params['seed']}", thread_ts)
            for image in resp.json()['images']:
                im = Image.open(BytesIO(base64.b64decode(image)))
                send_img(slack_token, slack_channel, im, thread_ts)
        else:
            print(f"Fail to generate girl: {resp.text}")
    except Exception as e:
        print(f"Fail to generate girl:", e)
        print(traceback.format_exc())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--gpt-token", type=str, help="Token for chat gpt", required=True)
    parser.add_argument("--slack-token", required=False)
    parser.add_argument("--slack-channel", required=False)

    args, _ = parser.parse_known_args(sys.argv)
    proc = subprocess.Popen(" ".join(["./webui.sh",  "--api"] + ([f"'{arg}'" for arg in sys.argv[1:]])), shell=True)
    try:
        wait_for_launch()

        print("stable diffusion webui launched")

        chat_gpt = ChatGTP(args.gpt_token)
        while True:
            generate_girl(chat_gpt, args.slack_token, args.slack_channel)
            time.sleep(10)
    finally:
        proc.kill()
