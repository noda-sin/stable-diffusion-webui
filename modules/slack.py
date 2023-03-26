from modules.shared import cmd_opts
from slack_sdk import WebClient
import uuid
import PIL
import io

def send_txt(text: str):
    token = cmd_opts.slack_token
    channel = cmd_opts.slack_channel

    if not token:
        return

    client = WebClient(token=token)
    try:
        client.chat_postMessage(channel=channel, text=text)
    except Exception as e:
        print(f"Fail to send text: {e}")


def send_img(img: PIL.Image):
    token = cmd_opts.slack_token
    channel = cmd_opts.slack_channel

    if not token:
        return

    client = WebClient(token=token)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    try:
        client.files_upload(channels=[channel], filename=f"{uuid.uuid4()}.png", file=img_bytes.getvalue())
    except Exception as e:
        print(f"Fail to send image: {e}")
