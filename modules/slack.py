from modules.shared import cmd_opts
from slack_sdk import WebClient
import uuid
import PIL
import io

def send_img(img: PIL.Image):
    token = cmd_opts.slack_token
    channel = cmd_opts.slack_channel

    if not token:
        return

    client = WebClient(token=token)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    client.files_upload(channels=[channel], filename=f"{uuid.uuid4()}.png", file=img_bytes.getvalue())
