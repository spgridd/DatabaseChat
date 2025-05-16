from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from architecture.chat_history import ChatHistory, Instructions
from typing import Dict, List, Any
from pydantic import BaseModel, ConfigDict
import json


load_dotenv()

with open("src/data/ddl_schema.sql") as f:
    ddl_schema = f.read()

with open("src/data/restrurants_schema.ddl") as f:
    restaurants = f.read()


class ChatClient():
    def __init__(self):
        self.client = genai.Client(
            vertexai=True,
            project=os.getenv("GEMINI_PROJECT"),
            location=os.getenv("GEMINI_LOCATION")
        )
        self.instructions = Instructions()


    def generate_data(self, prompt, ddl_schema, temperature, max_tokens):
        """
        Generate data using short prompts.
        """
        system_instruction = self.instructions.get_generate_config(ddl=ddl_schema)
        if not prompt:
            prompt = "1-5 rows for each table"

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="application/json"
            )
        )

        print(f"\n TOKENS: {response.usage_metadata} \n")

        return response.text
    
    
    def edit_data(self, prompt, dataframes, temperature, max_tokens):
        """
        Edit existing data using prompts.
        """
        system_instruction = self.instructions.get_edit_config(dataframes=dataframes)
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="application/json"
            )
        )

        return response.text

    
    def clear_history(self):
        """
        Clear history of the chat to start again without exiting.
        """
        self.history = ChatHistory()