from openai import OpenAI
import string
import random

def uuid(length=16):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

class CallAi:
    def __init__(self,api_key,base_url,model=None):
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(
            api_key = api_key,
            base_url= base_url,
        )
        self.model =  model if model else 'qwen-plus'
        self._prompt = ""
        self.inquiry = ""

    @property
    def prompt(self):
        return self._prompt

    @prompt.setter
    def prompt(self,content):
        self._prompt = content

    def chat(self,text,top_p = 0.9, temperature = 0.7):
        completion = self.client.chat.completions.create(
            model= self.model,
            messages=[
                {'role': 'system', 'content': f'{self._prompt}'},
                {'role': 'user', 'content': text}],
            temperature = temperature,
            top_p = top_p
        )
        reply = completion.choices[0].message.content
        return reply