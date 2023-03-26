import subprocess
import time
import requests
import chat_gpt
import remote_config
import sys
import argparse
import copy
import random

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

def generate_girl(gpt_token):
    try:
        txt = generate_girl_txt(gpt_token)
        quote = chat_gpt.generate_quote(gpt_token, txt)
        params = remote_config.config().copy()
        params["prompt"] = params["prompt"] + f"{lora()}(({txt}))"
        print("Start to generate girl", params)
        resp = requests.post(url="http://127.0.0.1:7860/sdapi/v1/txt2img", json=params)
        if resp.status_code == 200:
            print(f"Success to generate girl: {txt}")
        else:
            print(f"Fail to generate girl: {resp.text}")
    except Exception as e:
        print(f"Fail to generate girl", e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--gpt-token", type=str, help="Token for chat gpt", required=True)
    args, _ = parser.parse_known_args(sys.argv)
    proc = subprocess.Popen(" ".join(["./webui.sh",  "--api"] + ([f"'{arg}'" for arg in sys.argv[1:]])), shell=True)
    try:
        wait_for_launch()

        print("stable diffusion webui launched")
        while True:
            generate_girl(args.gpt_token)
            time.sleep(10)
    finally:
        proc.kill()