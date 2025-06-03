from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from typing import Dict, List, Any
from pydantic import BaseModel, ConfigDict
import json
import logging
from sqlalchemy import create_engine, text
import pandas as pd
from langfuse import Langfuse

from architecture.chat_history import ChatHistory, Instructions
from functions.parse_ddl import parse_multiple_schemas
from functions.validation import validate_json
from functions.sql_generation import generate_query
from functions.plot_generation import generate_plot


load_dotenv()

logging.basicConfig(level=logging.INFO)


class SafetyResponse(BaseModel):
    is_safe: bool


class ChatClient():
    def __init__(self):
        self.client = genai.Client(
            vertexai=True,
            project=os.getenv("GEMINI_PROJECT"),
            location=os.getenv("GEMINI_LOCATION")
        )
        self.langfuse = Langfuse(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            host="https://cloud.langfuse.com"
        )
        self.instructions = Instructions()
        self.history = ChatHistory()

        self.is_safe = False

        self.validation_tool = types.Tool(
            function_declarations=[{
                "name": "validate_inputs",
                "description": "Validate whether input has correct types and informations.", #improve this - remove from system prompt
                "parameters": {
                    "type": "object",
                    "properties": {
                        "schema": {
                            "type": "string",
                            "description": "Schema with informations about data."
                        },
                        "data": {
                            "type": "object",
                            "description": "JSON data object to validate."
                        }
                    },
                    "required": ["schema", "data"]
                }
            }]
        )

        self.talk_tools = types.Tool(
            function_declarations=[
            {
                "name": "generate_query",
                "description": "Generate SQL query from user prompt.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_query": {
                            "type": "string",
                            "description": "Corrected prompt of the user for better understanding."
                        }           
                    },
                    "required": ["user_query"]
                }
            },
            {
                "name": "create_plot",
                "description": "Create plot from user prompt.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_query": {
                            "type": "string",
                            "description": "Corrected prompt of the user for better understanding."
                        }           
                    },
                    "required": ["user_query"]
                }
            }]
        )

    def talk_with_data(self, user_query, ddl_schema, contents):
        # Add some cleaning of the history
        contents.append(types.Content(parts=[types.Part(text=user_query)], role='user'))
        system_instruction = self.instructions.get_talk_config()

        self.history.add_message(role='user', content=user_query)

        config={
            "system_instruction": system_instruction,
            "temperature": 0.0,
            "tools": [self.talk_tools],
            "tool_config": {"function_calling_config": {"mode": "any"}}
        }

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=config
        )

        candidate = response.candidates[0]
        part = candidate.content.parts[0]
        # response_text = part.text

        for part in candidate.content.parts:
            call = getattr(part, "function_call", None)
            if call:
                logging.info("\nFunction Called\n")
                contents.append(types.Content(parts=[types.Part(function_call=call)], role='model'))
                if call.name == "generate_query":
                    dummy_query = call.args["user_query"]
                    logging.info(f"\nENHANCED QUERY:\n{dummy_query}\n")

                    error = 'first_run'
                    retries = 0

                    while error and retries < 5:
                        result = generate_query(client=self.client, user_query=user_query, ddl_schema=ddl_schema, error=error, contents=contents, for_plot=False)
                        query, dataframe, error, contents = result
                        retries += 1
                    
                    if retries >= 5:
                        return "ERROR"

                    self.history.add_message(role='assistant', content=(query, dataframe))

                    return query, dataframe, contents
                
                elif call.name == "create_plot":
                    error_plot = 'first_run'
                    while error_plot:
                        error = 'first_run'
                        while error:
                            result = generate_query(client=self.client, user_query=user_query, ddl_schema=ddl_schema, error=error, contents=contents, for_plot=True)
                            query, dataframe, error, contents = result

                        path, error_plot, contents = generate_plot(client=self.client, user_query=user_query, ddl_schema=ddl_schema, df=dataframe, error=error_plot, contents=contents)
                    
                    self.history.add_message(role='assistant', content=path)
                    
                    return path, contents


    def update_safety_flag(self, response):
        decoded = json.loads(response)
        decoded = decoded["is_safe"]

        if decoded:
            self.is_safe = True
        else:
            self.is_safe = False


    def check_safety(self, prompt):
        contents = [types.Content(parts=[types.Part(text=f"Check safety of this prompt:\n{prompt}")], role='user')]
        system_instruction = self.instructions.get_safety_config()
        
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.0,
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=SafetyResponse
            )
        )

        response_text = response.candidates[0].content.parts[0].text

        if response_text.startswith("```json"):
            response_text = response_text[len("```json"):].strip()
        if response_text.endswith("```"):
            response_text = response_text[:-3].strip()

        logging.info(f"\n\nSafety verdict:\n{response_text}\n\n")

        self.update_safety_flag(response=response_text)
    

    def get_table_names(self, ddl_schema: str) -> List[str]:
        parsed = parse_multiple_schemas(ddl_schema)
        return list(parsed.keys())


    def generate_data(self, prompt, ddl_schema, temperature, max_tokens):
        """
        Generate data for all tables, one at a time, and combine results.
        """
        system_instruction = self.instructions.get_generate_config()

        full_prompt = (
            f"DDL schema:\n{ddl_schema}\n\n"
            f"Prompt: {prompt}'\n"
        )

        self.check_safety(prompt=full_prompt)

        if self.is_safe:

            contents = [
                types.Content(parts=[types.Part(text=full_prompt)], role="user")
            ]

            response = self.client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature
                )
            )

            response_text = response.text

            if response_text.startswith("```json"):
                response_text = response_text[len("```json"):].strip()
            if response_text.endswith("```"):
                response_text = response_text[:-3].strip()

            return response_text
        
        else:
            logging.info("\n\nSTH NOT SAFE!!!\n\n")


    def extract_affected_tables(self, prompt: str, table_names: List[str]) -> List[str]:
        """
        Use LLM to extract affected table names from prompt.
        """
        system_instruction = "Extract and return a JSON list of table names affected by the instruction."

        contents = [
            types.Content(parts=[
                types.Part(text=f"Instruction: {prompt}\nTables: {', '.join(table_names)}")
            ], role="user")
        ]

        self.check_safety(prompt=prompt)

        if self.is_safe:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.0,
                    response_mime_type="application/json"
                )
            )

            try:
                return json.loads(response.text)
            except Exception as e:
                logging.warning(f"Could not extract affected tables: {e}")
                return table_names

    
    def edit_data(self, prompt, dataframes, temperature, max_tokens):
        """
        Edit only the relevant tables based on the prompt, return full dataset with updated tables.
        """
        all_tables = list(dataframes["data"].keys())
        logging.info(f"\n\n{all_tables}\n\n")
        affected_tables = self.extract_affected_tables(prompt, all_tables)
        logging.info(f"\n\n{affected_tables}\n\n")

        self.check_safety(prompt=prompt)

        if self.is_safe:
            # Subset of relevant tables
            partial_data = {"data": {
                table: dataframes["data"][table]
                for table in affected_tables if table in dataframes["data"]
            }}

            system_instruction = self.instructions.get_edit_config(json_schema=partial_data)
            # Call model with prompt and only affected tables
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=[types.Content(parts=[types.Part(text=prompt)], role="user")],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature,
                    response_mime_type="application/json"
                )
            )

            # candidate = response.candidates[0]
            # parts = candidate.content.parts[0]
            response_text = response.text

            try:
                edited_partial = json.loads(response_text)

                full_data = dataframes["data"].copy()

                # Replace only affected tables
                for table, new_data in edited_partial.get("data", {}).items():
                    full_data[table] = new_data

                return json.dumps({"data": full_data})

            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error during edit: {e}")
                return json.dumps(dataframes)  # return original

    
    def clear_history(self):
        """
        Clear history of the chat to start again without exiting.
        """
        self.history = ChatHistory()