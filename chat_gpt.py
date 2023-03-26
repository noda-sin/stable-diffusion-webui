import openai
import time
import argparse

queue = []

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

messages = [
    {"role": "user", "content": prompt},
]

def ask_to_gpt(gpt_token):
    if len(queue) > 0:
        return queue.pop()

    openai.api_key = gpt_token
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    messages.append({
        "role": "assistant", "content": response.choices[0].message.content,
    });
    messages.append({
        "role": "user", "content": "Next",
    });
    
    for line in response.choices[0].message.content.splitlines():
        if line.startswith('A:'):
            suggestion = line.replace('A:', '').strip()
            if len(suggestion) > 0:
                queue.append(suggestion)
    return queue.pop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--gpt-token", type=str, help="Token for chat gpt", required=True)
    args = parser.parse_args()
    while True:
        print(ask_to_gpt(args.gpt_token))
        time.sleep(1)
