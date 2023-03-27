import subprocess
import time
import requests
import remote_config
import sys
import argparse
import random
from PIL import Image
from io import BytesIO
import base64
import traceback

from chat_gpt import ChatGTP
from slack import Slack

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


def generate_girl(chat_gpt: ChatGTP, slack: Slack):
    try:
        txt = chat_gpt.get_params()
        quote = chat_gpt.get_quote(txt)
        params = remote_config.config().copy()
        params["prompt"] = params["prompt"] + f"{lora()}(({txt}))"
        print("Start to generate girl", params)
        resp = requests.post(url="http://127.0.0.1:7860/sdapi/v1/txt2img", json=params)

        if resp.status_code == 200:
            json = resp.json()
            print(f"Success to generate girl: {txt}")
            thread_ts = slack.send_message(quote)
            print(json['parameters'])
            slack.send_message(f"""
prompt: {params['prompt']}
seed: {json['parameters']['seed']}
""", thread_ts)
            print(json['parameters'])
            for image in json['images']:
                im = Image.open(BytesIO(base64.b64decode(image)))
                slack.send_image(im, thread_ts)
        else:
            print(f"Fail to generate girl: {resp.text}")
    except Exception as e:
        print(f"Fail to generate girl:", e)
        print(traceback.format_exc())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--gpt-token", type=str, help="Token for chat gpt", required=True)

    args, _ = parser.parse_known_args(sys.argv)
    proc = subprocess.Popen(" ".join(["./webui.sh",  "--api"] + ([f"'{arg}'" for arg in sys.argv[1:]])), shell=True)
    try:
        wait_for_launch()

        print("stable diffusion webui launched")

        chat_gpt = ChatGTP(args.gpt_token)
        slack = Slack()
        while True:
            generate_girl(chat_gpt, slack)
            time.sleep(10)
    finally:
        proc.kill()
