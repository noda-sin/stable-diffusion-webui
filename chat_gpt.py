import openai
import os

DEFAULT_MESSAGES = [
    {"role": "user", "content": """
Make a prompt describing a photo scene with a single famale model.
The scene should be one that, upon seeing the photo, takes your breath away.
Focus on the model what she is wearing, theme and the art style.
"""},
]

openai.api_key = os.environ.get('GPT_TOKEN')

class ChatGPT(object):
    instance = None
    params_queue = []

    def __new__(cls, *args, **kwargs):
        if cls.instance == None:
            cls.instance = super().__new__(cls)
        return cls.instance


    def __request(self, messages):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        return response.choices[0].message.content


    def get_params(self):
        return self.__request(DEFAULT_MESSAGES)


    def get_next_params(self, prev, ask):
        messages = DEFAULT_MESSAGES.copy()
        messages.append({
            "role": "assistant", "content": prev
        })
        messages.append({
            "role": "user", "content": ask
        })
        return self.__request(messages)
