import requests
import os
import json

with open(os.path.join(os.getcwd(), "templates.json")) as f:
    config = json.load(f)

def config():
    try:
        config = requests.get("https://raw.githubusercontent.com/noda-sin/stable-diffusion-webui/master/templates.json").json()
        return config
    except Exception as e:
        print("Failed to get remote config:", e)
        return config
