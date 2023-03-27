import openai
import time
import argparse

queue = []

messages_queue = [
    {"role": "user", "content": """
I will write a beautiful girl in AI and post it on Twitter every day. Each time we will change different background, clothes, expression, hairstyle, hair color, camera angle, shot and pose.
Shot is one of them (a close-up of face shot, an upper shot, a full body shot, shot from above, shot from below).
Can you think of a subject and suggest one?
Suggestions should be comma-separated and each item should be in English (word for word expressions, if at all possible).
You may use fictional backgrounds and clothing from games, anime, etc.

例1: Magical floating island background, fantasy RPG mage robe, focused spellcasting, twin-tail hair, purple and blue gradient hair, top-down angle, a close-up of face shot, wielding magic wand
例2: Underwater city background, futuristic underwater suit, curious smile, see-through bangs, translucent blue hair, diagonal front angle, a close-up of eyes shot, swimming underwater
例3: Nighttime food stall background, casual summer outfit, appetizing expression, side braid hair, honey blonde hair, profile angle, a head shot, holding takoyaki
例4: Cafe terrace background, casual spring outfit, cheerful smile, bob cut hair, caramel brown hair, diagonal front angle, an upper shot, holding a coffee cup
例5: Snowy forest background, warm winter coat, wide-eyed surprise, braided hair, ice blue hair, diagonal rear angle, a full body shot, holding a snowflake
例6: Treetop village background, elf warrior armor, brave stance, braided long hair, forest green hair, front angle, shot from above, holding a bow
例7: Desert oasis background, ethnic dress, dreamy expression, long wavy hair, sandy gold hair, diagonal front angle, shot from below, a full body shot, shading forehead with hand
例8: Space station background, astronaut suit, serious gaze, short cut hair, silver hair, profile angle, an upper shot, operating spacecraft control panel

Suggestions should be written after 'A:'.
"""},
]

def generate_girl_params(token):
    if len(queue) > 0:
        return queue.pop()

    replay = request_to_gpt(token, messages_queue)

    if (len(messages_queue) > 10):
        messages_queue = [messages_queue[0]]

    messages_queue.append({
        "role": "assistant", "content": replay,
    });
    messages_queue.append({
        "role": "user", "content": "Next",
    });
    
    for line in replay.splitlines():
        if line.startswith('A:'):
            suggestion = line.replace('A:', '').strip()
            if len(suggestion) > 0:
                queue.append(suggestion)
    return queue.pop()


def generate_quote(token, txt):
    replay = request_to_gpt(token, [
        {
            "role": "user", "content": f"""
以下の状況における美少女が言いそうなセリフを日本語で１つ考えてください（日本語）。

{txt}

提案は、A: の後に続けてください。
"""
        }]
    )
    for line in replay.splitlines():
            if line.startswith('A:'):
                suggestion = line.replace('A:', '').replace('「', '').replace('」', '').strip()
                if len(suggestion) > 0:
                    return suggestion
    return None


def request_to_gpt(token, messages):
    openai.api_key = token
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--token", type=str, help="Token for chat gpt", required=True)
    args = parser.parse_args()
    while True:
        params = generate_girl_params(args.token)
        quote = generate_quote(args.token, params)
        print(f"{params}: {quote}")
        time.sleep(1)
