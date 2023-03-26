import subprocess
import time
import requests
import chat_gpt
import sys
import argparse

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
    txt = chat_gpt.ask_to_gpt(gpt_token)
    while txt is None:
        time.sleep(10)
        txt = chat_gpt.ask_to_gpt()
    print(f"generated txt by chatGPT: {txt}")
    return txt

def generate_girl(gpt_token, batch):
    try:
        txt = generate_girl_txt(gpt_token)
        params = {
            "enable_hr": False,
            "denoising_strength": 0,
            "firstphase_width": 0,
            "firstphase_height": 0,
            "hr_scale": 2,
            "hr_upscaler": "string",
            "hr_second_pass_steps": 0,
            "hr_resize_x": 0,
            "hr_resize_y": 0,
            "prompt": f"best quality ,masterpiece, illustration, an extremely delicate and beautiful, extremely detailed ,CG ,unity ,8k wallpaper, Amazing, finely detail, masterpiece,best quality,official art,extremely detailed CG unity 8k wallpaper,absurdres, incredibly absurdres, huge filesize , ultra-detailed, extremely detailed, beautiful detailed girl, extremely detailed eyes and face, beautiful detailed eyes, (RAW photo, best quality), (realistic, photo-realistic:1.37), 1girl,cute,((very small breasts)),smiling,<lora:japaneseDollLikeness_v10:0.3>, (({txt}))",
            "negative_prompt": "nippless, paintings, sketches, (worst quality:2), (low quality:2), (normal quality:2), lowres, normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, age spot, glan,nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet,extra fingers,fewer fingers,strange fingers,bad han,hands",
            "styles": [
            ],
            "seed": 1319104494,
            "subseed": -1,
            "subseed_strength": 0,
            "seed_resize_from_h": -1,
            "seed_resize_from_w": -1,
            "sampler_name": "DPM++ SDE Karras",
            "batch_size": batch,
            "n_iter": 1,
            "steps": 30,
            "cfg_scale": 7,
            "width": 512,
            "height": 512,
            "restore_faces": False,
            "tiling": False,
            "eta": 0,
            "s_churn": 0,
            "s_tmax": 0,
            "s_tmin": 0,
            "s_noise": 1,
            "override_settings": {},
            "override_settings_restore_afterwards": True,
            "script_args": [],
        }
        resp = requests.post(url="http://127.0.0.1:7860/sdapi/v1/txt2img", json=params)
        if resp.status_code == 200:
            print(f"Success to generate girl: {txt}")
        else:
            print(f"Fail to generate girl: {resp.text}")
    except Exception as e:
        print(f"Fail to generate girl", e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--batch", type=int, help="Batch size", default=1)
    parser.add_argument("--gpt-token", type=str, help="Token for chat gpt", required=True)
    args, _ = parser.parse_known_args(sys.argv)
    proc = subprocess.Popen(" ".join(["./webui.sh",  "--api"] + ([f"'{arg}'" for arg in sys.argv[1:]])), shell=True)
    try:
        wait_for_launch()

        print("stable diffusion webui launched")
        while True:
            generate_girl(args.gpt_token, args.batch)
            time.sleep(10)
    finally:
        proc.kill()