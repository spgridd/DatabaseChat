from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from architecture.chat_history import ChatHistory, Instructions


load_dotenv()

with open("src/data/ddl_schema.sql") as f:
    ddl_schema = f.read()


class ChatClient():
    def __init__(self):
        self.instructions = Instructions()
        self.client = genai.Client(
            vertexai=True,
            project=os.getenv("GEMINI_PROJECT"),
            location=os.getenv("GEMINI_LOCATION")
        )
        self.chat = self.client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=self.instructions.system_config,
                temperature=0.7
            )
        )


    def ask_gemini(self, prompt):
        """
        Ask gpt model given question and receive answer.
        """
        response = self.chat.send_message(prompt)

        return response.text

    
    def clear_history(self):
        """
        Clear history of the chat to start again without exiting.
        """
        self.history = ChatHistory()