import subprocess
import time
import requests
import openai
import sys
import argparse

def ask_to_gpt(gpt_token):
    openai.api_key = gpt_token
    prompt = """
I will write a beautiful girl in AI and post it on Twitter every day. Each time we will change different background, clothes, expression, hairstyle, hair color, camera angle and pose. Can you think of a subject and suggest one?
Suggestions should be comma-separated and each item should be in English (word for word expressions, if at all possible).
You may use fictional backgrounds and clothing from games, anime, etc.

例1: Magical floating island background, fantasy RPG mage robe, focused spellcasting, twin-tail hair, purple and blue gradient hair, top-down angle, wielding magic wand
例2: Underwater city background, futuristic underwater suit, curious smile, see-through bangs, translucent blue hair, diagonal front angle, swimming underwater
例3: Nighttime food stall background, casual summer outfit, appetizing expression, side braid hair, honey blonde hair, profile angle, holding takoyaki
例4: Cafe terrace background, casual spring outfit, cheerful smile, bob cut hair, caramel brown hair, diagonal front angle, holding a coffee cup
例5: Snowy forest background, warm winter coat, wide-eyed surprise, braided hair, ice blue hair, diagonal rear angle, holding a snowflake
例6: Treetop village background, elf warrior armor, brave stance, braided long hair, forest green hair, front angle, holding a bow
例7: Desert oasis background, ethnic dress, dreamy expression, long wavy hair, sandy gold hair, diagonal front angle, shading forehead with hand
例8: Space station background, astronaut suit, serious gaze, short cut hair, silver hair, profile angle, operating spacecraft control panel

Suggestions should be written after 'A:'.
"""
    model = "text-davinci-002"
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=100
    )
    for line in response.choices[0].text.splitlines():
        if line.startswith('A:'):
            suggestion = line.replace('A:', '').strip()
            if len(suggestion) > 0:
                return suggestion
    return None

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
    txt = ask_to_gpt(gpt_token)
    while txt is None:
        time.sleep(10)
        txt = ask_to_gpt()
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
            "prompt": f"upper body,best quality ,masterpiece, illustration, an extremely delicate and beautiful, extremely detailed ,CG ,unity ,8k wallpaper, Amazing, finely detail, masterpiece,best quality,official art,extremely detailed CG unity 8k wallpaper,absurdres, incredibly absurdres, huge filesize , ultra-detailed, extremely detailed, beautiful detailed girl, extremely detailed eyes and face, beautiful detailed eyes, (RAW photo, best quality), (realistic, photo-realistic:1.37), 1girl,cute,((very small breasts)),smiling,<lora:japaneseDollLikeness_v10:0.3>, (({txt}))",
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