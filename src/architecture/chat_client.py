from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from typing import Dict, List, Any
from pydantic import BaseModel, ConfigDict
import json
import logging
from sqlalchemy import create_engine
import pandas as pd

from architecture.chat_history import ChatHistory, Instructions
from functions.parse_ddl import parse_multiple_schemas
from functions.validation import validate_json


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

        self.sql_tool = types.Tool(
            function_declarations=[{
                "name": '',
                "description": "",
                "parameters": {
                    "type": "",
                    "properties": {
                        "user_query": {
                            "type": "",
                            "description": ""
                        },
                        "ddl_schema": {
                            "type": "",
                            "description": ""
                        }             
                    },
                    "required": ["user_query", "ddl_schema"]
                }
            }]
        )

    def sql_generation(self, user_query, ddl_schema):
        # Add some cleaning of the history
        contents = [types.Content(parts=[types.Part(text=f"Generate SQL query for this setup.\nDDL schema: {ddl_schema}.\nUser query: {user_query}")], role='user')]
        system_instruction = self.instructions.get_sql_config()

        self.history.add_message(role='user', content=user_query)

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0
            )
        )

        user = os.getenv("POSTGRESQL_USER")
        password = os.getenv("POSTGRESQL_PASSWORD")
        db = os.getenv("POSTGRESQL_DB")
        engine = create_engine(f"postgresql+psycopg2://{user}:{password}@localhost:5432/{db}")

        response_text = response.candidates[0].content.parts[0].text

        if response_text.startswith("```sql"):
            response_text = response_text[len("```sql"):].strip()
        if response_text.endswith("```"):
            response_text = response_text[:-3].strip()

        with engine.connect() as connection:
            df = pd.read_sql(response_text, connection)

        self.history.add_message(role='assistant', content=(response_text, df))

        return response_text, df



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
                model="gemini-2.0-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=[self.validation_tool],
                    temperature=temperature
                )
            )

            candidate = response.candidates[0]
            part = candidate.content.parts[0]
            response_text = part.text

            for part in candidate.content.parts:
                # logging.info(f"Response Part: {part}")
                call = getattr(part, "function_call", None)
                if call:
                    logging.info("Function call found.")
                    if call.name == "validate_inputs":
                        schema = call.args["schema"]
                        data = call.args["data"]

                        # Validate
                        schema = parse_multiple_schemas(schema)
                        is_valid, errors = validate_json(schema, data)

                        if not is_valid:
                            logging.info("NOT VALID")
                            return self.generate_data(
                                prompt=f"Validation failed due to: {errors}. Please correct the JSON.",
                                ddl_schema=ddl_schema,
                                temperature=temperature,
                                max_tokens=max_tokens
                            )
                        else:
                            logging.info("VALID")


            if response_text.startswith("```json"):
                response_text = response_text[len("```json"):].strip()
            if response_text.endswith("```"):
                response_text = response_text[:-3].strip()

            # try:
            #     parsed = json.loads(response_text)
            #     if "data" in parsed and table in parsed["data"]:
            #         result_data[table] = parsed["data"][table]
            #     else:
            #         result_data[table] = parsed.get(table, parsed)
            # except json.JSONDecodeError as e:
            #     logging.warning(f"Failed to parse response for table {table}: {e}")
            #     continue

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
                model="gemini-2.0-flash",
                contents=[types.Content(parts=[types.Part(text=prompt)], role="user")],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature,
                    response_mime_type="application/json"
                )
            )

            candidate = response.candidates[0]
            parts = candidate.content.parts[0]
            response_text = parts.text

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