from openai import OpenAI
import os
from dotenv import load_dotenv
from architecture.chat_history import ChatHistory

print(os.getcwd)

with open("src/data/ddl_schema.sql") as f:
    ddl_schema = f.read()

load_dotenv()

class ChatClient():
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.history = ChatHistory()


    def ask_gpt(self, prompt):
        """
        Ask gpt model given question and receive answer.
        """
        self.history.add_message(role='user', content=prompt)

        messages = self.history.get_history()

        response_stream = self.client.chat.completions.create(
            model='gpt-4.1-mini',
            messages=messages
            # stream=True
        )

        # full_response = ""
        # for chunk in response_stream:
        #     delta = chunk.choices[0].delta
        #     content = delta.content if delta.content else ""
        #     full_response += content
        #     yield content

        self.history.add_message(role='assistant', content=response_stream.choices[0].message.content)

        return response_stream.choices[0].message.content

    
    def clear_history(self):
        """
        Clear history of the chat to start again without exiting.
        """
        self.history = ChatHistory()