from openai import OpenAI
import os
from dotenv import load_dotenv
from chat_history import ChatHistory

load_dotenv()

class ChatClient():
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.history = ChatHistory()
        self.history.add_message(role='system', content='You are a helpful assistant.')

    def ask_gpt(self, prompt):
        """
        Ask gpt model given question and receive answer.
        """
        self.history.add_message(role='user', content=prompt)

        messages = self.history.get_history()

        response = self.client.chat.completions.create(
            model='gpt-4.1-mini',
            messages=messages
        )

        self.history.add_message(role='assistant', content=response.choices[0].message.content)

        return response.choices[0].message.content
    
    def clear_history(self):
        """
        Clear history of the chat to start again without exiting.
        """
        self.history.clear_history()
        self.history.add_message(role='system', content='You are a helpful assistant.')